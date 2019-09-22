from dateutil import parser
import datetime as dt

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

def trial_from_response_data(response_data):
    trial_model = {
        new_key: response_data.get(old_key) for new_key, old_key in RESPONSE_TO_TRIAL_MAP.items()
    }

    for time_field in DATE_FIELDS:
        if trial_model.get(time_field):
            trial_model[time_field] = parser.parse(trial_model[time_field]).isoformat()
    return trial_model
