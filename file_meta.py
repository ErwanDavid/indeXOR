
import hashlib
import os
from datetime import datetime
from datetime import timezone
import eyed3
import pikepdf
import docx
import exifread
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

extImage = ['jpg','jpeg','png', 'gif']

def sha256sum(filename):
    try:
        h  = hashlib.sha256()
        b  = bytearray(128*1024)
        mv = memoryview(b)
        with open(filename, 'rb', buffering=0) as f:
            for n in iter(lambda : f.readinto(mv), 0):
                h.update(mv[:n])
        logging.debug(f"Calculated SHA256 for {filename}")
        return h.hexdigest()
    except Exception as e:
        logging.error(f"Failed to calculate SHA256 for {filename}: {e}")
        return None

def getMetaDatafromDoc(doc):
    metadata = {}
    prop = doc.core_properties
    metadata["author"] = prop.author
    metadata["category"] = prop.category
    metadata["comments"] = prop.comments
    metadata["content_status"] = prop.content_status
    metadata["created"] = prop.created
    metadata["identifier"] = prop.identifier
    metadata["keywords"] = prop.keywords
    metadata["last_modified_by"] = prop.last_modified_by
    metadata["language"] = prop.language
    metadata["modified"] = prop.modified
    metadata["subject"] = prop.subject
    metadata["title"] = prop.title
    metadata["version"] = prop.version
    return metadata

def GetfromMp3(fullfile):
    try:
        audio = eyed3.load(fullfile)
        mp3info= {}
        mp3info['artist'] = audio.tag.artist
        mp3info['album']  = audio.tag.album
        mp3info['title']  = audio.tag.title
        logging.debug(f"Extracted MP3 metadata from {fullfile}")
        return mp3info
    except Exception as e:
        logging.error(f"Failed to extract MP3 metadata from {fullfile}: {e}")
        return {}

def GetfromPdf(fullfile):
    try:
        pdf = pikepdf.Pdf.open(fullfile)
        docinfo = pdf.docinfo
        objReturn = {}
        for key, value in docinfo.items():
            objReturn[key] = str(value)
        logging.debug(f"Extracted PDF metadata from {fullfile} {objReturn}")
        return objReturn
    except Exception as e:
        logging.error(f"Failed to extract PDF metadata from {fullfile}: {e}")
        return {}
    
def GetfromDoc(fullfile):
    try:
        doc = docx.Document(fullfile) 
        metadata_dict = getMetaDatafromDoc(doc)
        logging.debug(f"Extracted DOCX metadata from {fullfile}")
        return metadata_dict
    except Exception as e:
        logging.error(f"Failed to extract DOCX metadata from {fullfile}: {e}")
        return {}

def GetfromExif(fullfile):
    return_exif = {}
    try :
        f = open(fullfile, 'rb')        # open for meta
    except :
        logging.error(f"Failed to open file for EXIF: {fullfile}")
        return ''
    try:
        tags = exifread.process_file(f, details=False)
        if 'JPEGThumbnail' in tags.keys():
            tags["JPEGThumbnail"] = ''
        for tag in tags.keys():
            if tag != 'JPEGThumbnail' : 
                tag_key = tag.replace(' ','_')
                return_exif[tag_key] = str(tags[tag])[:100]  
        logging.debug(f"Extracted EXIF data from {fullfile}")
        return return_exif
    except :
        logging.error(f"Failed to process EXIF for file: {fullfile}")
        return False

def dateFromExif(exifObj):
    dayfolder = ''
    for tag in exifObj:
        if 'DateTimeOriginal' in tag:
            logging.debug(f"Found DateTimeOriginal in EXIF: {tag} - {exifObj[tag]}")
            datestr = str(exifObj[tag])
            if datestr.find("/") > 0:
                dayfolder = datestr.replace('/','_').replace(' ', '-')
            else:
                dayfolder = datestr.replace(':','_').replace(' ', '-')
    return dayfolder

def dateFromMtime(mtimeFile):
    dateTimeFile = datetime.fromtimestamp(mtimeFile, tz=timezone.utc)
    logging.debug(f"Found date from mtime: {dateTimeFile}")
    return dateTimeFile.strftime("%Y_%m")

def isImage(extention) :
    if  extention  in extImage:
        return True
    else :
        return False

def isMp3(extention) :
    extMp3 = ['mp3', 'wav']
    if  extention  in extMp3:
        return True
    else :
        return False

def isPdf(extention) :
    extPdf = ['pdf']
    if  extention  in extPdf:
        return True
    else :
        return False

def isDoc(extention) :
    extDoc = ['docx']
    if  extention  in extDoc:
        return True
    else :
        return False

class FileMeta:
    def __init__(self, fullfile):
        logging.info(f"Processing file: {fullfile}")
        self.fullfile = fullfile
        self.extention = fullfile.split('.')[-1].lower()
        self.filename = fullfile.split('/')[-1]
        self.filesize = os.path.getsize(fullfile)
        self.mtime = os.path.getmtime(fullfile)
        self.sha256sum = sha256sum(fullfile)
        if isImage(self.extention) :
            self.dayfolder = dateFromExif(self.exif)
            self.exif = GetfromExif(fullfile)
        else :
            self.dayfolder = dateFromMtime(self.mtime)
        if isMp3(self.extention) :
            self.mp3info = GetfromMp3(fullfile)
        if isPdf(self.extention) :
            self.pdfinfo = GetfromPdf(fullfile)
        if isDoc(self.extention) :
            self.docinfo = GetfromDoc(fullfile)
        logging.info(f"Finished processing file: {fullfile}")

    def getJsonRepresentation(self):
        return self.__dict__

    