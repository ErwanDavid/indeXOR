import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def getFileList(folder,allowed_ext) :
    fileList = []
    logging.info(f"Scanning folder {folder} for files with extensions {allowed_ext}")
    for root, dirs, files in os.walk(folder):
        for file in files:
            if any(file.endswith(ext) for ext in allowed_ext):
                fileList.append(os.path.join(root, file))
    logging.info(f"Found {len(fileList)} files in folder {folder} with allowed extensions")
    return fileList