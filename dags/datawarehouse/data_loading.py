#responsibekl to for loadin, reading and parsing json

import json
from datetime import date
import logging

logger = logging.getLogger(__name__)

def load_data(): # fix this up 
    
    file_path = f"./data/YT_data{date.today()}.json" #there might need ot be a _ in betweent he data and {}
    
    try:
        logger.info(f"Processing file: YT_data{date.today()}")
        
        with open(file_path,"r",encoding="utf-8") as raw_data:
            data = json.load(raw_data)
            
        return data #shoudl be fine on small data, or use ijson
    
    except FileNotFoundError:
        logger.error(f"File not found:{file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file:{file_path}")
        raise
        