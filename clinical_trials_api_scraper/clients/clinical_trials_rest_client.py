import requests
import logging
from dateutil import parser

logger = logging.getLogger(__name__)


class ClinicalTrialsRestClient(object):
    base_url = "https://clinicaltrials.gov/api"
    # Limited to 20 fields without challenge
    DEFAULT_REQUESTED_FIELDS = [
        "BriefTitle",
        # "Condition",
        # "CompletionDate", # Only slightly different than primary completion date which is main concern
        "DelayedPosting",
        "DesignPrimaryPurpose",
        "LastUpdateSubmitDate",
        "LocationCountry",
        "IsFDARegulatedDrug",
        "IsUnapprovedDevice",
        "IsUSExport",
        "NCTId",
        # "OfficialTitle",
        "OrgClass",
        "OrgFullName",
        # "OverallOfficialAffiliation",
        # "OverallOfficialName",
        "OverallStatus",
        "Phase",
        # "PointOfContactEMail",
        # "PointOfContactOrganization",
        "PrimaryCompletionDate",
        "PrimaryCompletionDateType",
        # "ResponsiblePartyInvestigatorFullName",
        "ResultsFirstPostDate",
        "ResultsFirstSubmitDate",
        "StartDate",
        "StudyType",
        # "StatusVerifiedDate",
        # "WhyStopped",
    ]
    MAX_REQUESTABLE_RECORDS = 1000

    @classmethod
    def get_max_study_id(cls):
        request_url = "{}/query/study_fields?fmt=JSON".format(cls.base_url)
        response = requests.get(request_url)
        response.raise_for_status()
        return response.json()["StudyFieldsResponse"]["NStudiesAvail"]

    @classmethod
    def request_trials(
        cls, start_id, end_id=None, requested_fields=None, dry_run=False
    ):
        if start_id < 1:
            raise IndexError("start_id must be 1 or greater: {}".format(start_id))

        if (end_id + 1 - start_id) > cls.MAX_REQUESTABLE_RECORDS:
            raise IndexError(
                "Requested more records than {} records: [{}, {}]".format(
                    cls.MAX_REQUESTABLE_RECORDS, start_id, end_id
                )
            )

        requested_fields = requested_fields or cls.DEFAULT_REQUESTED_FIELDS
        request_url = "{api_url}/query/study_fields?fmt=JSON&fields={fields}&min_rnk={min_rnk}".format(
            api_url=cls.base_url, fields=",".join(requested_fields), min_rnk=start_id,
        )
        if end_id:
            request_url = "{request_url}&max_rnk={max_rnk}".format(
                request_url=request_url, max_rnk=end_id,
            )
        if dry_run:
            return request_url
        response = requests.get(request_url)
        return cls._clean_response(response)

    @classmethod
    def _clean_response(cls, response):
        response.raise_for_status()
        response_data = cls._extract_data(response)
        return cls._clean_data(response_data)

    @classmethod
    def _extract_data(cls, response):
        json_response = response.json()["StudyFieldsResponse"]
        if json_response["NStudiesReturned"] == 0:
            return []
        data_version = json_response["DataVrs"]
        response_data = json_response["StudyFields"]
        for datum in response_data:
            datum["DataVersion"] = parser.parse(data_version)
        return response_data

    @classmethod
    def _clean_data(cls, response_data):
        """
        Trial data is all returned as a list but should just be a single value or None
        :param response_data: List of dicts with trial data
        :return: response_data with inner values unwrapped
        """
        for trial in response_data:
            for default_field in cls.DEFAULT_REQUESTED_FIELDS:
                if default_field in trial:
                    field_value = trial[default_field]
                    if isinstance(field_value, (list, tuple)):
                        # TODO: just take the first one for now, this is a hack!
                        trial[default_field] = (
                            field_value[0] if len(field_value) > 0 else None
                        )
            # delete useless field
            del trial["Rank"]
        return response_data
