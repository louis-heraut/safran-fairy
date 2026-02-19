#!/usr/bin/env python3

get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from art import tprint

from safran_fairy import download, decompress, split, convert, merge, upload, clean


## CONFIGURATION _______________
RESOURCES_DIR = Path.cwd() / "resources"
CONFIG_FILE = RESOURCES_DIR / "config.json"

def load_config(CONFIG_FILE):
    """Charge la configuration depuis config.json"""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

config = load_config(CONFIG_FILE)
load_dotenv()


WELCOME_FILE = RESOURCES_DIR / config['welcome_file']
STATE_FILE = RESOURCES_DIR / config['state_file']
METADATA_VARIABLES_FILE = RESOURCES_DIR / config['metadata_variables_file']

DOWNLOAD_DIR = config['download_dir']
RAW_DIR = config['raw_dir']
SPLIT_DIR = config['split_dir']
CONVERT_DIR = config['convert_dir']
OUTPUT_DIR = config['output_dir']

METEO_BASE_URL = config['meteo_base_url']
METEO_DATASET_ID = config['meteo_dataset_id']

RDG_BASE_URL = config['rdg_base_url']
RDG_DATASET_DOI = config['rdg_dataset_doi']
RDG_API_TOKEN = os.getenv("RDG_API_TOKEN")

metadata_variables = pd.read_csv(METADATA_VARIABLES_FILE,
                                 index_col='variable')


## RUN _____________
def main():
    with open(WELCOME_FILE, 'r') as f:
        print(f.read())
    
    # 1. Téléchargement
    downloaded_files = download(STATE_FILE, DOWNLOAD_DIR,
                                METEO_BASE_URL, METEO_DATASET_ID)
    
    if not downloaded_files:
        print("\n✨ Rien de nouveau à traiter!")
        return
    
    # 2. Dézipage
    decompressed_files = decompress(DOWNLOAD_DIR, RAW_DIR,
                                    downloaded_files)
        
    # 3. Traitement
    splited_files = split(RAW_DIR, SPLIT_DIR, decompressed_files)

    # 4. Conversion NetCDF
    converted_files = convert(SPLIT_DIR, CONVERT_DIR,
                              metadata_variables, splited_files)

    # 5. Concaténer
    merged_files = merge(CONVERT_DIR, OUTPUT_DIR, converted_files)

    # 6. Upload
    merged_files = list(Path(OUTPUT_DIR).glob("*latest*.nc"))
    merged_files= [Path("04_SAFRAN-data_output/DLI_QUOT_SIM2_previous-19580801-20260131.nc")]
    file_categories = [[f.stem.split('_QUOT_SIM2_')[0],
                        f.stem.split('_QUOT_SIM2_')[1].split('-')[0]]
                       for f in merged_files]
    
    not_uploaded = upload(dataset_DOI=RDG_DATASET_DOI,
                          OUTPUT_DIR=OUTPUT_DIR,
                          file_paths=merged_files,
                          file_categories=file_categories,
                          overwrite=False,
                          RDG_BASE_URL=RDG_BASE_URL,
                          RDG_API_TOKEN=RDG_API_TOKEN)

    
# if __name__ == "__main__":
    # main()
