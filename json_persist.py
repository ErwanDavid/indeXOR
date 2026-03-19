import json


def add_to_json_file(data, json_out_file):
    try:
        with open(json_out_file, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []
        print(f"**** Creating new JSON file: {json_out_file}")
    existing_data.append(data)
    with open(json_out_file, 'w') as f:
        json.dump(existing_data, f, indent=4, default=str)


def exists(fullfile, json_out_file):
    try:
        with open(json_out_file, 'r') as f:
            existing_data = json.load(f)
            for item in existing_data:
                if item['path'] == fullfile:
                    return True
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    return False

def get_all(json_out_file, N=10):
    try:
        with open(json_out_file, 'r') as f:
            existing_data = json.load(f)
            return existing_data
    except(FileNotFoundError, json.JSONDecodeError):
        return False
    return False

def get_all_content(json_out_file, N=10):

    data = []
    with open(json_out_file, 'r') as f:
        for line in f:
            cur_dic=json.loads(line)
            if cur_dic['content'] and len(cur_dic['content']) > 4 :
                data.append(cur_dic)
    return data
    # except(FileNotFoundError, json.JSONDecodeError):
    #     return False
    # return False


class Persist:
    def __init__(self, json_out_file):
        self.json_out_file = json_out_file
    def get_all(self):
        return get_all_content(self.json_out_file)
    def add(self, data):
        add_to_json_file(data, self.json_out_file)
    def exists(self, fullfile):
        return exists(fullfile, self.json_out_file)
