import os

def getFileList(folder):
    fileList = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            fileList.append(os.path.join(root, file))
    return fileList