import json
import file_meta as fm
import pprint as pp
import folder_tools as ft

json_out_file = "meta.json"

def add_to_json_file(data, json_out_file):
    try:
        with open(json_out_file, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []
    existing_data.append(data)
    with open(json_out_file, 'w') as f:
        json.dump(existing_data, f, indent=4)


folder = "/net/epstein_files/"
fileList = ft.getFileList(folder)
for file in fileList: 
    print("file", file)
    meta = fm.FileMeta(file)
    add_to_json_file(meta.getJsonRepresentation(), json_out_file)