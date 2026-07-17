
import hashlib
import os
import logging
import subprocess
import file_meta  as fm
from bs4 import BeautifulSoup
import spacy
# python -m spacy download en_core_web_sm

# Load the pre-trained model
nlp = spacy.load('en_core_web_sm')

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_file_content_txt(fullfile):
    try:
        with open(fullfile, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            logging.debug(f"  ***  extracted text content length: {len(content)} characters")
            return content
    except Exception as e:
        logging.error(f"Failed to extract text content from TXT file {fullfile}: {e}")
        return '' 

def get_file_content_html(fullfile):
    try:
        with open(fullfile, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
            # Use BeautifulSoup to parse HTML and extract text
            
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text(separator=' ', strip=True)
            logging.debug(f"  ***  extracted HTML content length: {len(text_content)} characters")
            return text_content
    except Exception as e:
        logging.error(f"Failed to extract text content from HTML file {fullfile}: {e}")
        return ''

def get_file_content_pdf(fullfile):
    # run java external tool to extract text content from pdf
    #cmd = f"/usr/bin/java -jar tika-app-3.2.3.jar -t '{fullfile}' -"
    # use subprocess.run instead of os.popen
    cmd = [
        "java",
        "-cp",
        "tika-app-3.2.3.jar:jai-imageio-core-1.4.0.jar",
        "org.apache.tika.cli.TikaCLI",
        "-t",
        fullfile,
    ]
    logging.debug(f"Running command to extract text content from PDF: {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,    # grab stdout/stderr
            text=True,              # return strings not bytes
            check=True              # raise CalledProcessError on non‑zero exit
        )
        output = proc.stdout
        logging.debug(f"  ***  extracted text content length: {len(output)} characters")
        return output
    except subprocess.CalledProcessError as e:
        logging.error(
            f"Failed to extract text content from PDF {fullfile}: "
            f"returncode={e.returncode} stderr={e.stderr}"
        )
    except Exception as e:
        logging.error(f"Unexpected error extracting text content from PDF {fullfile}: {e}")
    return ''

#extract all distinct non stop  word 
def extract_keywords(text):
    # Process the text with spaCy
    doc = nlp(text)
    # Create a frequency dictionary for non-stop words
    word_freq = {}
    for token in doc:
        if not token.is_stop and not token.is_punct and token.is_alpha:
            word = token.lemma_.lower()  # Use lemma to group similar words
            word_freq[word] = word_freq.get(word, 0) + 1
    # Sort the words by frequency and get the top N keywords
    sorted_keywords = sorted(word_freq.items(), key=lambda item: item[1], reverse=True)
    top_keywords = [word for word, freq in sorted_keywords]
    return top_keywords

def extract_entities(bio_text):
    doc = nlp(bio_text)
    ret_dic_clean = {}
    entity_lookup = {}

    # Build entities with all sentence numbers (1-based) where they are found.
    for sent_num, sent in enumerate(doc.sents, start=1):
        for ent in sent.ents:
            key = (ent.label_, ent.text)
            if key in entity_lookup:
                if sent_num not in entity_lookup[key]["sent"]:
                    entity_lookup[key]["sent"].append(sent_num)
            else:
                entry = {"entity": ent.text, "sent": [sent_num]}
                ret_dic_clean.setdefault(ent.label_, []).append(entry)
                entity_lookup[key] = entry
    return ret_dic_clean

class FileContent:
    def __init__(self, fullfile):
        self.fullfile = fullfile
        self.extention = fullfile.split('.')[-1].lower()
        self.content = ''

    def getContent(self):
        logging.info(f"Extracting content from file: {self.fullfile} with extension: {self.extention}")
        if fm.isImage(self.extention)  or fm.isPdf(self.extention) or fm.isDoc(self.extention):
            self.content = get_file_content_pdf(self.fullfile)
        if fm.isTxt(self.extention) :
            self.content = get_file_content_txt(self.fullfile)
        if fm.isHtml(self.extention) :
            self.content = get_file_content_html(self.fullfile)
        if self.content:
                self.content = self.content.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        logging.debug(f"Extracted content length: {len(self.content)} characters")
        return self.content
    
    def extract_entities(self):
        return extract_entities(self.content)