from dateutil import parser

RESPONSE_TO_TRIAL_MAP = {
    'id': 'NCTId',
    # 'trialId': 'NCTId',
    'orgName': 'OrgFullName',
    'orgType': 'OrgClass',
    'completionStatus': 'OverallStatus',
    'isDelayed': 'DelayedPosting',
    'completionDate': 'CompletionDate',
    'resultsReportDate': 'ResultsFirstSubmitDate',
    'contactEmail': 'PointOfContactEMail',
    'clinicaltrialsUpdatedAt': 'DataVersion',
    # '': 'StatusVerifiedDate',
    # '': 'ResultsFirstSubmitQCDate',
    # '': 'ResultsFirstPostDate',
    # '': 'ResultsFirstPostDateType',
    # '': 'CompletionDateType',
    # '': 'WhyStopped',
}
DATE_FIELDS = ['completionDate', 'clinicaltrialsUpdatedAt']

INSTITUTION_FIELDS = ['orgName', 'orgType']


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
    trial_model = {
        new_key: response_data.get(old_key) for new_key, old_key in RESPONSE_TO_TRIAL_MAP.items()
    }
    trial_model['isDelayed'] = trial_model.get('isDelayed') == 'Yes'

    for time_field in DATE_FIELDS:
        if trial_model.get(time_field):
            trial_model[time_field] = parser.parse(
                trial_model[time_field]).isoformat()
    return trial_model


def dict_to_snake_case(d):
    return {to_snake_case(k): v for k, v in d.items()}


def to_snake_case(str):

    return ''.join(['_'+i.lower() if i.isupper()
                    else i for i in str]).lstrip('_')
