from dateutil import parser

# fields not in this map just get passed through
RENAME_FIELDS_MAP = {
    'NCTId': 'id',
}
DATE_FIELDS = ['completionDate', 'clinicaltrialsUpdatedAt']

INSTITUTION_FIELDS = ['org_full_name', 'org_class']


def extract_institution_from_trial(trial):
    institution = {}
    for field in INSTITUTION_FIELDS:
        institution[field] = trial.pop(field)
    return institution


def split_institution_trial(full_trial):
    trial = full_trial.copy()
    institution = {}
    for field in INSTITUTION_FIELDS:
        value = trial.pop(field)
        value = '' if value is None else value
        institution[field] = value
    return institution, trial


def trial_from_response_data(response_data):
    trial_model = {RENAME_FIELDS_MAP.get(
        k, k): v for k, v in response_data.items()}

    for k, v in trial_model.items():
        if not isinstance(v, str):
            continue

        # convert anything that parses as a date into a date in ISO format
        try:
            trial_model[k] = parser.parse(v).isoformat()
            continue
        except ValueError:
            pass

        # convert anything that looks boolean into a bool
        if v == 'Yes':
            trial_model[k] = True
            continue
        elif v == 'No':
            trial_model[k] = False
            continue

        # convert integers (I'm not aware of any floats in the schema)
        try:
            trial_model[k] = int(v)
            continue
        except ValueError:
            pass

    return dict_to_snake_case(trial_model)


def dict_to_snake_case(d):
    return {to_snake_case(k): v for k, v in d.items()}


def to_snake_case(str):
    return ''.join(['_'+i.lower() if i.isupper()
                    else i for i in str]).lstrip('_')
