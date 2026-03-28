# indeXOR
indeXOR: a tool to index you FS into either json, mongodb, orELK

## Requirements

pip install python_docx pikepdf magika eyed3 ExifRead spacy
python -m spacy download en_core_web_sm

JAVA jre 17+ for tika
eg: 
pacman -Sy jre-openjdk

## Feature

multi process
get mime type & type description
extract exif tags from images
extract pdf tags
extract docx tags
extract mp3 tags
compute SHA256

## Purpose

Sort file (duplicate by SHA256, aggregate by path, date ...)
Get distinct metadata like authors (doc, pdf, mp3), camera, ...
Create stats on mime types
