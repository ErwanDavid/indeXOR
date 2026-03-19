
import json_persist as persist
import elastic_persist as elk_persist
import argparse
import spacy
import logging
# python -m spacy download en_core_web_sm

# Load the pre-trained model
nlp = spacy.load('en_core_web_sm')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_entities(bio_text):
    doc = nlp(bio_text)
    ret_dic_clean={}
    for ent in doc.ents:
        if ent.label_ in ret_dic_clean.keys():
            if ent.text not in ret_dic_clean[ent.label_]:
                ret_dic_clean[ent.label_].append(ent.text)
        else:
            ret_dic_clean[ent.label_] = []
            ret_dic_clean[ent.label_].append(ent.text)
    return ret_dic_clean

parser = argparse.ArgumentParser(description='')
parser.add_argument('-f', '--file', help=' ', required=True)
parser.add_argument('-i', '--index', help=' ', required=True)
args = parser.parse_args()

file_src = args.file
file_persist_src = persist.JsonPersist(file_src)
persist_dst = elk_persist.ElasticPersist('https://localhost:9200',args.index)

logging.info(f"Enriching data from file: {file_src} and indexing to ElasticSearch index: {args.index}")
for data in file_persist_src.get_all() :
    entities= extract_entities(data['content'])
    data['entities'] = entities
    persist_dst.add(data)
    logging.info(f"{data['path']}")
    #print(f"______________\n{data['content']} ->-> \n{entities}" )