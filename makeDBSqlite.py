#!/usr/bin/env python
# -*- coding: utf-8 -*-

import exifread
import docx
import pikepdf
import eyed3
from magika import Magika

import re
import json
import pathlib, hashlib
import multiprocessing as mp
import sqlite3
from datetime import datetime, timezone
import time
import argparse


parser=argparse.ArgumentParser(description="indeXOR: a tool to index you FS",
                               epilog='Will create a DB at indicated file destination')
parser.add_argument("path", help="path to be scanned eg /home/truc/")
parser.add_argument("DBFilepath", help="Database file (sqlite) eg /data/mydb.db")
args=parser.parse_args()


m = Magika()


def createTable(cursor_obj):
    print("CREATE TABLE")
    cursor_obj.execute("DROP TABLE IF EXISTS FILE")
    table = """ CREATE TABLE FILE (
                sha256  VARCHAR(255) NOT NULL,
                path  VARCHAR(255) NOT NULL,
                file  VARCHAR(255) NOT NULL,
                extention CHAR(25) NOT NULL,
                mimetype VARCHAR(25) NOT NULL,
                typedesc VARCHAR(100) NOT NULL,
                size int NOT NULL,
                mtime real,
                month VARCHAR(25) NOT NULL,
                year int NOT NULL,
                all_author VARCHAR(250),
                img_camera VARCHAR(250),
                img_focallengh VARCHAR(250),
                mp3_title VARCHAR(250),
                mp3_album VARCHAR(250),
                meta VARCHAR(50000)
            ); """
    cursor_obj.execute(table)


def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

def getMetaData(doc):
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
    audio = eyed3.load(fullfile)
    mp3info= {}
    mp3info['artist'] = audio.tag.artist
    mp3info['album']  = audio.tag.album
    mp3info['title']  = audio.tag.title
    return mp3info

def GetfromPdf(fullfile):
    pdf = pikepdf.Pdf.open(fullfile)
    docinfo = pdf.docinfo
    objReturn = {}
    for key, value in docinfo.items():
        objReturn[key] = value
    #print("pdf", objReturn)
    return objReturn
    
def GetfromDoc(fullfile):
    doc = docx.Document(fullfile) 
    metadata_dict = getMetaData(doc)
    #print("Docx", metadata_dict)
    return metadata_dict

def GetfromExif(fullfile):
    return_exif = {}
    try :
        f = open(fullfile, 'rb')        # open for meta
    except :
        return ''
    try:
        tags = exifread.process_file(f, details=False)
        if 'JPEGThumbnail' in tags.keys():
            tags["JPEGThumbnail"] = ''
        for tag in tags.keys():
            #print(tag, "\t",str(tags[tag])[:30])
            if tag != 'JPEGThumbnail' : 
                tag_key = tag.replace(' ','_')
                return_exif[tag_key] = str(tags[tag])[:100]  
        #print("exif", return_exif)     
        return return_exif
    except :
        return False

def dateFromExif(exifObj):
    dayfolder = ''
    for tag in exifObj:
        if 'DateTimeOriginal' in tag:
            #print('  date found in exif', tag, "\t",str(exifObj[tag]))
            datestr = str(exifObj[tag])
            if datestr.find("/") > 0:
                dayfolder = datestr.replace('/','_').replace(' ', '-')
            else:
                dayfolder = datestr.replace(':','_').replace(' ', '-')
    return dayfolder

def dateFromMtime(mtimeFile):
    #print('  date from mtime ', mtimeFile, "\t")
    dateTimeFile = datetime.fromtimestamp(mtimeFile, tz=timezone.utc)
    return dateTimeFile.strftime("%Y_%m")

def isImage(extention) :
    extImage = ['jpg','jpeg','png', 'gif']
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

def AddEntry(cursor_obj,sha256, path, file, extention, typedesc, mimetype, size, mtime, \
                month, year, all_author, img_camera, img_focallengh, mp3_title, mp3_album, meta):
    conn.execute('''INSERT INTO FILE (sha256, path, file, extention,typedesc, mimetype, size, mtime, month, year, all_author, img_camera, img_focallengh, mp3_title, mp3_album, meta)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',    (sha256, path, file, extention,typedesc, mimetype, size, mtime, month, year, all_author, img_camera, img_focallengh, mp3_title, mp3_album, meta))
    conn.commit()

def myWork(filePath):
    print(getTimeStr(), "START", str(filePath))
    metaStr = ''
    appModel = ''
    focalLengh = ''
    author = ''
    exif = ''
    mp3_album= ''
    mp3_title= ''
    DocObj = ''
    PdfObj = ''
    Mp3Obj = ''
    res = m.identify_path(filePath)
    type_desc = res.output.description
    mime = res.output.mime_type
    mtime = filePath.stat().st_mtime
    folderdate= dateFromMtime(mtime)
    extention = filePath.suffix.lower().replace('.', '')
    filename = filePath.name
    foldername = str(filePath.parent)
    size = filePath.stat().st_size
    print(getTimeStr(), "  META", str(filePath))
    try:
        if isImage(extention) :
            exif = GetfromExif(str(filePath))
            folderdate = dateFromExif(exif)
            if 'Image_Model' in exif.keys():
                appModel = exif['Image_Model']
                appModel = re.sub(r"\s+", "_", appModel)
                appModel = re.sub(r"_$", "", appModel)
                appModel = re.sub(r"[^0-9A-Za-z\-_]+", "", appModel)
                appModel = appModel[:30]
            if 'EXIF_FocalLengthIn35mmFilm' in exif.keys():
                focalLengh = exif['EXIF_FocalLengthIn35mmFilm']

        if isDoc(extention) :
            DocObj=GetfromDoc(str(filePath))
            if 'author' in DocObj.keys():
                author = DocObj['author']
        if isPdf(extention) :
            PdfObj=GetfromPdf(str(filePath))
            if '/Creator' in PdfObj.keys():
                author = str(PdfObj['/Creator']) 
            if '/Author' in PdfObj.keys():
                author = str(PdfObj['/Author']) 
        if isMp3(extention) :
            Mp3Obj=GetfromMp3(str(filePath))
            if 'artist' in Mp3Obj.keys():
                author = Mp3Obj['artist']
            if 'album' in Mp3Obj.keys():
                mp3_album = Mp3Obj['album']
            if 'title' in Mp3Obj.keys():
                mp3_title = Mp3Obj['title']
    except :
        print("Error on metadata extraction")

    print(getTimeStr(), "  SHA", str(filePath))
    sha256 = sha256sum(str(filePath))
    month = folderdate[:7]
    year = folderdate[:4]
    metaStr=str(exif) + str(DocObj) + str(PdfObj) + str(Mp3Obj)
    #sha256, path, file, extention, size, mtime, month, year, all_author, img_camera, img_focallengh, mp3_title, mp3_album, meta
    print(getTimeStr(), "  INSERT", str(filePath))
    AddEntry(QueryCurs, sha256,foldername, filename, extention, type_desc, mime,size,mtime,\
            month,year, author, appModel, focalLengh,\
            mp3_title, mp3_album, metaStr)    



def get_all_path(directory):
    print("    _get_all_path from", directory)
    Todo = []
    for path in sorted(pathlib.Path(directory).rglob('*')):
        if path.is_file() :
            #print("\tAdding on ",str(path))
            Todo.append(path)
    return Todo

def getTimeStr():
    return time.strftime("%Y%m%d-%H%M%S")

def needCreate():
    listOfTables = QueryCurs.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='FILE' ''').fetchall()
    print(len(listOfTables))
    if len(listOfTables) > 0:
        return False 
    else:
        return True

conn = sqlite3.connect(args.DBFilepath)
QueryCurs = conn.cursor()
#if needCreate() :
createTable(QueryCurs)

pool = mp.Pool(mp.cpu_count())
#pool = mp.Pool(1)
global_Todo =  get_all_path(args.path)
print("BIG LIST : ", len(global_Todo))
results = pool.map(myWork, [row for row in global_Todo], 2)
