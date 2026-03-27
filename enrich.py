
import json_persist as persist
import elastic_persist as elk_persist
import argparse
import spacy
import logging
#from transformers import pipeline
#from flair.nn import Classifier
#from flair.data import Sentence

# load the model
#tagger = Classifier.load('ner')
# python -m spacy download en_core_web_sm

# Load the pre-trained model
nlp = spacy.load('en_core_web_sm')
#ner_pipeline = pipeline("ner")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def extract_entities_bert(bio_text):
#     entities = ner_pipeline(bio_text)
#     ret_dic_clean={}
#     for ent in entities:
#         if ent['entity'] in ret_dic_clean.keys():
#             if ent['word'] not in ret_dic_clean[ent['entity']]:
#                 ret_dic_clean[ent['entity']].append(ent['word'])
#         else:
#             ret_dic_clean[ent['entity']] = []
#             ret_dic_clean[ent['entity']].append(ent['word'])
#     return ret_dic_clean

# def extract_entities_flair(bio_text):
#     sentence = Sentence(bio_text)
#     tagger.predict(sentence)
#     ret_dic_clean={}
#     for entity in sentence.get_spans('ner'):
#         if entity.get_label('ner').value in ret_dic_clean.keys():
#             if entity.text not in ret_dic_clean[entity.get_label('ner').value]:
#                 ret_dic_clean[entity.get_label('ner').value].append(entity.text)
#         else:
#             ret_dic_clean[entity.get_label('ner').value] = []
#             ret_dic_clean[entity.get_label('ner').value].append(entity.text)
#     return ret_dic_clean

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

def find_kw(text, kw):
    # find pair with the keyword and the word after it
    kw_list = []
    words = text.split()
    for i in range(len(words)-1):
        if words[i].lower() == kw.lower():
            kw_list.append(words[i] + " " + words[i+1])
    return kw_list

parser = argparse.ArgumentParser(description='')
parser.add_argument('-f', '--file', help=' ', required=True)
parser.add_argument('-i', '--index', help=' ', required=True)
args = parser.parse_args()

file_src = args.file
file_persist_src = persist.Persist(file_src)
persist_dst = elk_persist.Persist('https://localhost:9200',args.index)

logging.info(f"Enriching data from file: {file_src} and indexing to ElasticSearch index: {args.index}")
for data in file_persist_src.get_all() :
    file_content = data['content'].replace('\n', ' ')[0:10000]
    entities= extract_entities(file_content)
    #entities = extract_entities_bert(file_content)
    #entities = extract_entities_flair(file_content)

    project_list = find_kw(file_content, "project")
    defendant_list = find_kw(file_content, "defendant")
    data['entities'] = entities
    data['projects'] = project_list
    data['defendants'] = defendant_list
    persist_dst.add(data)
    logging.info(f"{data['path']}")
    logging.info(f"______________\n{data['content']} ->-> \n{entities}" )