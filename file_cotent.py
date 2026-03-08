
import hashlib
import os
import logging
import subprocess
import file_meta  as fm

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def get_file_content_img(fullfile):
    return None


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
    return None

class FileContent:
    def __init__(self, fullfile):
        self.fullfile = fullfile
        self.extention = fullfile.split('.')[-1].lower()
        self.content = None
        logging.info(f"Extracting content from file: {fullfile} with extension: {self.extention}")
        if fm.isImage(self.extention) :
            self.content = get_file_content_pdf(fullfile)
        if fm.isPdf(self.extention) :
            self.content = get_file_content_pdf(fullfile)
        if fm.isDoc(self.extention) :
            self.content = get_file_content_pdf(fullfile)

    def getContent(self):
        return self.content