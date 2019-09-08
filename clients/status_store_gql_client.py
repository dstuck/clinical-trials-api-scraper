import requests

# tmp
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

    def create_institution(self, institution_name, org_type):
        response_json = self.make_request(self._create_institution_query(
            institution_name,
            org_type
        ))
        return response_json['data']['createInstitution']['institution']['id']

    def get_all_institutions(self):
        response_json = self.make_request(self._get_all_institutions_query_str())
        return response_json['data']['allInstitutions']

    @staticmethod
    def _create_institution_query(institution_name, org_type):
        return '''mutation {{
      createInstitution(
        input: {{
          institution: {{
            orgName: "{}",
            orgType: "{}"
          }}
        }}
      ) {{
        institution {{
          id
          orgName
          orgType
        }}
      }}
    }}'''.format(institution_name, org_type)

    @staticmethod
    def _get_all_institutions_query_str():
        return '''query {
          allInstitutions {
            nodes {
              id
              orgName
              orgType
              trialsByOrgId {
                nodes {
                  id
                  completionDate
                  completionStatus
                  resultsReportDate
                }
              }
            }
          }
        }'''
