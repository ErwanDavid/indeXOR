from datetime import datetime
from elasticsearch import Elasticsearch



def add_to_elk(data, client, idx):
    data['id'] = data['_id']
    del data['_id']
    resp = client.index(index=idx, id=data['id'], document=data)
    return True

def exists(fullfile, json_out_file):
    return False

def get_all(json_out_file, N=10):
    return False

class Persist:
    def __init__(self, server, index):
        self.index_name = index
        self.client = Elasticsearch(server, verify_certs=False, basic_auth=('elastic', 'changeme'))
    #def get_all(self):
    #    return get_all(self.client)
    def add(self, data):
        add_to_elk(data, self.client, self.index_name)
    #def exists(self, fullfile):
    #    return exists(fullfile, self.client)
