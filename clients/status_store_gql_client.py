import requests

# TODO: productionize this hack
CONFIG = {
    'graphql': {
        'host': 'localhost',
        'port': '5000'
    }
}

class StatusStoreGqlClient(object):
    def __init__(self):
        self.api_endpoint = "http://{}:{}/graphql".format(
            CONFIG['graphql']['host'],
            CONFIG['graphql']['port']
        )
        self.headers = {}

    def make_request(self, query_str):
        response = requests.post(
            url=self.api_endpoint,
            json={'query': query_str},
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    def get_or_create_institution(self, institution_name, org_type):
        institution_id = self._get_institution(institution_name, org_type)
        if not institution_id:
            institution_id = self._create_institution(institution_name, org_type)
        return institution_id

    def _get_institution(self, institution_name, org_type):
        """
        Gets institution by name and type
        :param institution_name: org_name of institution
        :param org_type: org_type of institution
        :return: Id of institution if exists or None
        """
        response_json = self.make_request(self._get_institution_query_str(
            institution_name,
            org_type,
        ))
        edges = response_json['data']['allInstitutions']['edges']
        if not edges:
            return None
        elif len(edges) > 1:
            raise IndexError("Found more than one institution: {}".format(edges))
        return edges[0].get('node', {}).get('id')


    def _create_institution(self, institution_name, org_type):
        response_json = self.make_request(self._create_institution_query(
            institution_name,
            org_type
        ))
        return response_json['data']['createInstitution']['institution']['id']

    def get_all_institutions(self):
        response_json = self.make_request(self._get_all_institutions_query_str())
        return response_json['data']['allInstitutions']

    @staticmethod
    def _get_institution_query_str(institution_name, org_type):
        return '''query {{
          allInstitutions(
            condition:{{
              orgName: "{org_name}"
              orgType: "{org_type}"
            }}
          ) {{
            edges {{
              node {{
                id
              }}
            }}
          }}
        }}'''.format(org_name=institution_name, org_type=org_type)

    @staticmethod
    def _create_institution_query(institution_name, org_type):
        return '''mutation {{
      createInstitution(
        input: {{
          institution: {{
            orgName: "{org_name}",
            orgType: "{org_type}"
          }}
        }}
      ) {{
        institution {{
          id
          orgName
          orgType
        }}
      }}
    }}'''.format(org_name=institution_name, org_type=org_type)

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
