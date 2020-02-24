from dateutil import parser
import datetime as dt
import logging

logger = logging.getLogger(__name__)

# fields not in this map just get passed through
RENAME_FIELDS_MAP = {
    "NCTId": "id",
}

ORGANIZATION_FIELDS = ["org_full_name", "org_class"]
US_TERRITORIES = set([
    "United States",
    "American Samoa",
    "Guam",
    "Northern Mariana Islands",
    "Puerto Rico",
    "U.S. Virgin Islands"
])

def extract_institution_from_trial(trial):
    institution = {}
    for field in ORGANIZATION_FIELDS:
        institution[field] = trial.pop(field)
    return institution


def split_organization_trial(full_trial):
    trial = full_trial.copy()
    institution = {}
    for field in ORGANIZATION_FIELDS:
        value = trial.pop(field)
        value = "" if value is None else value
        institution[field] = value
    return institution, trial


def trial_from_response_data(response_data):
    trial_model = {RENAME_FIELDS_MAP.get(k, k): v for k, v in response_data.items()}

    for k, v in trial_model.items():
        if not isinstance(v, str):
            continue

        # convert date columns
        if  k.endswith("Date") and v is not None:
            trial_model[k] = parser.parse(v)
            continue

        # convert anything that looks boolean into a bool
        if v == "Yes":
            trial_model[k] = True
            continue
        elif v == "No":
            trial_model[k] = False
            continue

        # convert integers (I'm not aware of any floats in the schema)
        try:
            trial_model[k] = int(v)
            continue
        except ValueError:
            pass

    return dict_to_snake_case(trial_model)


def add_computed_fields(trial):
    """Adds Computed fields to a trial

    Fields related to https://clinicaltrials.gov/ct2/manage-recs/fdaaa
    should_have_results: the trial should have reported results by now
    is_late: the trial was late reporting results, but is not missing
    is_missing: the trial results should have been reported by now but are missing
    """
    add_applicable_trial_fields(trial)

    one_year = dt.timedelta(365)
    one_year_ago = trial["data_version"] - one_year
    # logger.info(trial)
    completion_date = trial["primary_completion_date"]
    is_applicable_trial = trial["is_applicable_trial"]
    trial["should_have_results"] = (
        is_applicable_trial and completion_date is not None and completion_date <= one_year_ago
    )

    results_date = trial["results_first_post_date"]
    if not trial['is_applicable_trial']:
        return trial

    trial["is_late"] = (
        trial["should_have_results"]
        and results_date is not None
        and results_date > (completion_date + one_year)
    )

    trial["is_missing"] = trial["should_have_results"] and not results_date

    trial["is_on_time"] = (
        trial["should_have_results"]
        and not trial["is_late"]
        and not trial["is_missing"]
    )

    return trial

def add_applicable_trial_fields(trial):
    """
    1) StudyType="Interventional"
    2) Any of:
        1) {"United States", "American Samoa", "Guam", "Northern Mariana Islands", "Puerto Rico", "U.S. Virgin Islands"} intersects with set(LocationCountry)
        2) [[Has IND or IDE Number]] - not publically available
        3) "Yes" in IsUSExport
    3) Either:
        1) IsFDARegulatedDrug and Phase != "Phase 1"
        2) IsUnapprovedDevice and DesignPrimaryPurpose != "Device Feasibility"

    :param trial: Trial dictionary
    :param rigorous: Whether to treat missing values as False (rigorous) or True (not rigorous)
    :return:
    """
    is_interventional = trial.get('study_type') == "Interventional"
    is_under_fda_oversight = (
        trial['location_country'] in US_TERRITORIES
        or trial['is_u_s_export']
    )
    is_major_drug_test = (
        trial['is_f_d_a_regulated_drug']
        and trial["phase"]
        and "Phase 1" not in trial["phase"]
    )
    is_major_device_test = (
        trial['is_unapproved_device']
        and trial["design_primary_purpose"] != "Device Feasibility"
    )
    trial['is_interventional'] = is_interventional
    trial['is_under_fda_oversight'] = is_under_fda_oversight
    trial['is_major_drug_test'] = is_major_drug_test
    trial['is_major_device_test'] = is_major_device_test
    trial['is_applicable_trial'] = (
        is_interventional
        and is_under_fda_oversight
        and (is_major_device_test or is_major_drug_test)
    )

def dict_to_snake_case(d):
    return {to_snake_case(k): v for k, v in d.items()}


def to_snake_case(str):
    return "".join(["_" + i.lower() if i.isupper() else i for i in str]).lstrip("_")
