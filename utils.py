import json

def import_params_from_json(json_file):
    with open(json_file, 'r') as f:
        params = json.load(f)
    return params