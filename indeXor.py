from datetime import datetime
import logging
import argparse
import file_meta as fm
import file_cotent as fc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
parser = argparse.ArgumentParser(description='Process INPUT (typically files) and store metadata/content \
                                 in OUTPUT (typically JSON or ElasticSearch)\
                                 example usage: \npython indeXor.py -t FileSystem -i /path/to/folder -T ElasticSearch -O my_index_url')
parser.add_argument('-t', '--inputType', help='Input source type (e.g., FileSystem, JSON)', required=True)
parser.add_argument('-i', '--inputUrl', help='Input source (e.g., folder path or JSON file)', required=True)
parser.add_argument('-T', '--outputType', help='Output destination type (e.g., JSON or ElasticSearch)', required=True)
parser.add_argument('-O', '--outputUrl', help='Output destination (e.g., JSON file path or ElasticSearch index name)', required=True)
args = parser.parse_args()
input_type = args.inputType
input_url = args.inputUrl
output_type = args.outputType
output_url = args.outputUrl

logging.info(f"Processing input: {input_url} of type {input_type}")
logging.info(f" and storing results in {output_url} of type {output_type}")

# OUTPUT TYPE HANDLING
if output_type.lower() == 'json':
    logging.info(f"Output type is JSON, processing accordingly")
    import json_persist as persist
elif output_type.lower() == 'elasticsearch':
    logging.info(f"Output type is ElasticSearch, processing accordingly")
    import elastic_persist as persist
elif output_type.lower() == 'mongodb':
    logging.info(f"Output type is MongoDB, processing accordingly")
    import mongodb_persist as persist
else:
    logging.error(f"Unsupported output type: {output_type}")

# INPUT TYPE HANDLING
if input_type.lower() == 'filesystem':
    logging.info(f"Input type is FileSystem, processing accordingly")
    import filesystem_input as input_handler
elif input_type.lower() == 'json':
    logging.info(f"Input type is JSON, processing accordingly")
    #import json_input as input_handler
else:
    logging.error(f"Unsupported input type: {input_type}")

allowed_ext = ['jpg','jpeg','png','bmp', 'gif', 'pdf', 'docx', 'doc', 'mp3', 'txt', 'wav', 'xlsx', 'pptx', 'xls', 'ppt', 'mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'webm']

outputHandler = persist.Persist(output_url)


fileList = input_handler.getFileList(input_url, allowed_ext)
for file in fileList:
        logging.info(f"________ Processing file: {file}")
        filejson = {}
        filejson['path'] = file
        filejson['scan_date'] = datetime.today().strftime("%Y-%m-%d")
        if not outputHandler.exists(file):
            meta = fm.FileMeta(file)
            filejson['meta'] = meta.getJsonRepresentation()
            content = fc.FileContent(file)
            filejson['content'] = content.getContent()
            if len(filejson['content']) > 4:
                filejson['entities'] = fc.extract_entities(filejson['content'])
            outputHandler.add(filejson)
        else:
            logging.info(f"File already processed, skipping: {file}")
