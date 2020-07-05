import pymongo

def get_raw_data(table):
    doc_count = table.count_documents(filter={})
    data = [dict(i) for i in table.find({}, {'_id':False})[0:doc_count]]
    return data
