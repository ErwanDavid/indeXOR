import logging
import file_meta as fm
import file_cotent as fc
import folder_tools as ft
import json_persist as persist
import datetime 


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

json_out_file = "test_2.json"
folder = "/home/erwan/Documents/tmp/"
allowed_ext = ['jpg','jpeg','png','bmp', 'gif', 'pdf', 'docx', 'doc', 'mp3', 'txt', 'wav', 'xlsx', 'pptx', 'xls', 'ppt', 'mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'webm']

fileList = ft.getFileList(folder, allowed_ext)
file_persist = persist.JsonPersist(json_out_file)
for file in fileList:
        logging.info(f"________ Processing file: {file}")
        filejson = {}
        filejson['path'] = file
        filejson['scan_date'] = datetime.date.today().strftime("%Y-%m-%d")
        if not file_persist.exists(file):
            meta = fm.FileMeta(file)
            filejson['meta'] = meta.getJsonRepresentation()
            content = fc.FileContent(file)
            filejson['content'] = content.getContent()
            logging.info(f"Adding file to JSON: {filejson}")
            file_persist.add(filejson)
        else:
            logging.info(f"File already processed, skipping: {file}")
  #  except Exception as e:
  #      print(f"Error processing file {file}: {e}")