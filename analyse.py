import pandas as pd
import logging
import argparse
import pprint as pp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


agg_list = [
    ['meta', 'extention'],
    ['meta', 'mimetype'],
    ['entities', 'ORG'],
    ['entities', 'PERSON']
]

def get_aggregations(df, mycol, limit=10):
    logging.debug(f"Getting aggregations for columns: {mycol}")
    final_agg = {}
    if mycol[0] in df.columns:
        logging.debug(f"Column {mycol[0]} found in DataFrame")
        #pp.pprint(df[mycol[0]].array)
        for obj in df[mycol[0]].array:
            #logging.debug(f"Value: {obj}")
            if isinstance(obj, dict) and mycol[1] in obj:
                val = obj[mycol[1]]
                if isinstance(val, list):
                    for item in val:
                        if item in final_agg.keys():
                            final_agg[item] += 1
                        else:
                            final_agg[item] = 1
                else:
                    if val in final_agg.keys():
                        final_agg[val] += 1
                    else:
                        final_agg[val] = 1
        sorted_agg = dict(sorted(final_agg.items(), key=lambda item: item[1], reverse=True))
        return dict(list(sorted_agg.items())[:limit])
    else:
        logging.warning(f"Column {mycol[0]} not found in DataFrame")
        return {}

#load json file to dataframe
def load_json_to_df(json_file):
    try:
        df = pd.read_json(json_file)
        logging.debug(f"Loaded JSON file {json_file} into DataFrame with {len(df)} records")
        return df
    except Exception as e:
        logging.error(f"Failed to load JSON file {json_file} into DataFrame: {e}")
        return pd.DataFrame()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyse JSON file and extract insights')
    parser.add_argument('-f', '--file', help='Path to the JSON file to analyze', required=True)
    parser.add_argument('-l', '--limit', type=int, help='Limit the number of top results to display', default=10)
    args = parser.parse_args()
    df = load_json_to_df(args.file)
    if not df.empty:
        logging.info(f"DataFrame loaded successfully with {len(df)} records")
        # Perform analysis on the DataFrame here
    else:
        logging.warning("DataFrame is empty, no analysis will be performed")
    for agg_tab in agg_list:
        agg = get_aggregations(df, agg_tab, limit=args.limit)
        print(f"Top {len(agg)} most common {agg_tab[1]}:")
        print(agg)
