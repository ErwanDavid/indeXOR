from pymongo import MongoClient

database = MongoClient ("mongodb://localhost:27017/")
db = database['scan_db_usb']


def exists(file, db_collection):
    return db_collection.find_one({"path": file}) is not None

def add(filejson, db_collection):
    db_collection.insert_one(filejson)

def get_all(db_collection, N=10):
    return db_collection.find().limit(N)


class Persist:
    def __init__(self, db_collection):
        self.collection = db[db_collection]
    def add(self, data):
        add(data, self.collection)
    def get_all(self):
        return get_all(self.collection)
    def exists(self, fullfile):
        return exists(fullfile, self.collection)


                        