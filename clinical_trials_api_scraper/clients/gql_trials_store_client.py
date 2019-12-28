import logging
import requests


from clinical_trials_api_scraper.clients.trials_store_interface_base import \
    TrialsStoreInterfaceBase
from clinical_trials_api_scraper.utils.trial_model_utils import (
    extract_institution_from_trial,
    trial_from_response_data,
)
from clinical_trials_api_scraper.utils.gql_utils import format_dict_as_gql_map

logger = logging.getLogger(__name__)


class GqlTrialsStoreClient(TrialsStoreInterfaceBase):
    def __init__(self, host, port):
        self.api_endpoint = "http://{}:{}/graphql".format(
            host,
            port
        )
        self.headers = {}

    def make_request(self, query_str):
        response = requests.post(
            url=self.api_endpoint,
            json={'query': query_str},
            headers=self.headers,
        )
        try:
            response.raise_for_status()
        except Exception as ex:
            logger.warning("Bad query: {}".format(query_str))
            raise ex
        return response.json()

    def is_ready(self):
        try:
            response = self.make_request(self._get_schema_query_str())
        except Exception as ex:
            logger.info("Connection exception: {}".format(ex.args))
            return False
        return True

    def store_trials_batch(self, trials_batch):
        trials = [trial_from_response_data(t) for t in trials_batch]
        self.create_or_update_trials_institutions(trials)

    def create_or_update_trials_institutions(self, trials):
        for trial in trials:
            trial['orgId'] = self.get_or_create_institution(
                extract_institution_from_trial(trial)
            )
        self._create_or_update_trials(trials)

    def _create_or_update_trials(self, trials):
        """
        Add or update trials given corresponding org_id
        :param trials:
        :return:
        """
        # For now implementing serially, potentially look into batch operations: https://github.com/graphile/postgraphile/issues/634
        for trial in trials:
            if self._get_trial(trial['id']):
                self._update_trial(trial)
            else:
                self._create_trial(trial)

    def _get_trial(self, trial_id):
        response = self.make_request(self._get_trial_query_str(trial_id))
        return response['data']['trialById']

    def _create_trial(self, trial):
        response = self.make_request(self._create_trial_query_str(trial))
        return response['data']['createTrial']['trial']['id']

    def _update_trial(self, trial):
        response = self.make_request(self._update_trial_query_str(trial))
        return response['data']['updateTrialById']['trial']['id']

    def get_or_create_institution(self, institution):
        institution_id = self._get_institution(institution)
        if not institution_id:
            institution_id = self._create_institution(institution)
        return institution_id

    def _get_institution(self, institution):
        """
        Gets institution by name and type
        :param institution: dict with institution fields
        :return: Id of institution if exists or None
        """
        response_json = self.make_request(
            self._get_institution_query_str(institution))
        edges = response_json['data']['allInstitutions']['edges']
        if not edges:
            return None
        elif len(edges) > 1:
            raise IndexError(
                "Found more than one institution: {}".format(edges))
        return edges[0].get('node', {}).get('id')

    def _create_institution(self, institution):
        response_json = self.make_request(self._create_institution_query_str(
            institution
        ))
        return response_json['data']['createInstitution']['institution']['id']

    def get_all_institutions(self):
        response_json = self.make_request(
            self._get_all_institutions_query_str())
        return response_json['data']['allInstitutions']

    @staticmethod
    def _get_schema_query_str():
        return '''{
          __schema {
            types {
              name
            }
          }
        }'''

    @staticmethod
    def _get_trial_query_str(trial_id):
        return '''query {{
          trialById(id:"{trial_id}") {{
            id
          }}
        }}'''.format(trial_id=trial_id)

    @staticmethod
    def _create_trial_query_str(trial):
        return '''mutation {{
      createTrial(
        input: {{
          trial: {}
        }}
      ) {{
        trial {{
          id
        }}
      }}
    }}'''.format(format_dict_as_gql_map(trial))

    @staticmethod
    def _update_trial_query_str(trial):
        trial_id = trial.pop('id')
        return '''mutation {{
      updateTrialById(
        input: {{
          trialPatch: {trial}
          id: "{trial_id}",
        }},
      ) {{
        trial {{
          id
        }}
      }}
    }}'''.format(trial_id=trial_id, trial=format_dict_as_gql_map(trial))

    @staticmethod
    def _get_institution_query_str(institution):
        return '''query {{
          allInstitutions(
            condition: {institution_map}
          ) {{
            edges {{
              node {{
                id
              }}
            }}
          }}
        }}'''.format(institution_map=format_dict_as_gql_map(institution))

    @staticmethod
    def _create_institution_query_str(institution):
        return '''mutation {{
      createInstitution(
        input: {{
          institution: {institution_map}
        }}
      ) {{
        institution {{
          id
          orgName
          orgType
        }}
      }}
    }}'''.format(institution_map=format_dict_as_gql_map(institution))

    @staticmethod
    def _get_all_institutions_query_str():
        return '''query {
          allInstitutions {
            nodes {
              id
              orgName
              orgType
              lateReportCount
              readyForReportCount
              lateReportRate
              trialsByOrgId {
                nodes {
                  id
                  completionDate
                  completionStatus
                  resultsReportDate
                  isLate
                  readyForReport
                }
              }
            }
          }
        }'''
