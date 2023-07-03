
def read_in_json(json_file):
    # read in json and parse into dictionaries
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data
