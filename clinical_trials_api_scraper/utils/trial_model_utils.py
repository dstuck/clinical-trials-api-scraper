RESPONSE_TO_TRIAL_MAP = {
    'NCTId': 'trialId',
    'OrgFullName': 'orgName',
    'OrgClass': 'orgType',
    'OverallStatus': 'completionStatus',
    # 'StatusVerifiedDate': '',
    'DelayedPosting': 'isDelayed',
    # 'WhyStopped': '',
    'CompletionDate': 'completionDate',
    # 'CompletionDateType': '',
    'ResultsFirstSubmitDate': 'resultsReportDate',
    # 'ResultsFirstSubmitQCDate': '',
    # 'ResultsFirstPostDate': '',
    # 'ResultsFirstPostDateType': '',
    'PointOfContactEMail': 'contactEmail',
    'DataVersion': 'clinicaltrialsUpdatedAt',
}

def trial_from_response_data(response_data):
    trial_model = {
        new_key: response_data.get(old_key) for old_key, new_key in RESPONSE_TO_TRIAL_MAP.items()
    }
    return trial_model
