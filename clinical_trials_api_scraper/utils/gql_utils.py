import json
import re

JSON_KEY_PATTERN = r'\"(\S+)\":'

def format_dict_as_gql_map(python_dict):
    quoted_key_json = json.dumps(python_dict)
    return re.sub(JSON_KEY_PATTERN, r'\1:', quoted_key_json)
