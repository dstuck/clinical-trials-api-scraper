from dateutil import parser
import datetime as dt
import logging

logger = logging.getLogger(__name__)

# fields not in this map just get passed through
RENAME_FIELDS_MAP = {
    "NCTId": "id",
}

ORGANIZATION_FIELDS = ["org_full_name", "org_class"]


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
        if "Date" in k and v is not None:
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
    one_year = dt.timedelta(365)
    one_year_ago = dt.datetime.now() - one_year
    # logger.info(trial)
    completion_date = trial["completion_date"]
    trial["should_have_results"] = (
        completion_date is not None and completion_date <= one_year_ago
    )

    results_date = trial["results_first_post_date"]
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


def dict_to_snake_case(d):
    return {to_snake_case(k): v for k, v in d.items()}


def to_snake_case(str):
    return "".join(["_" + i.lower() if i.isupper() else i for i in str]).lstrip("_")
