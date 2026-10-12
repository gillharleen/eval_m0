# Main file: set up logging, load csv data into postgres, then run reports.

import logging
import os
from dotenv import load_dotenv
from pathlib import Path

import ingestor
import analytics

# load values from .env to environment
load_dotenv()

# make logs folder in project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file_str = LOG_DIR / os.environ.get("LOG_FILE", "default.log")

# log level from .env, WARNING if not set
log_level_str = os.environ.get("LOG_LEVEL", "WARNING").upper()

# logging setup for all files
logging.basicConfig(filename=log_file_str,
                    format='%(asctime)s %(levelname)s [%(filename)s]: %(message)s',
                    filemode='a')

# set level for all loggers, then get logger for this file
logger = logging.getLogger()
logger.setLevel(log_level_str)

logger = logging.getLogger(__name__)

# runs only when this file is run directly
if __name__ == "__main__":

    # read csv files and load into db
    logger.info("CSV processing started")
    ingestor.ingest_csv("src/input_files")
    logger.info("CSV processing finished")

    # run Analytics reports
    logger.info("Running Analytics queries...")
    analytics.show_analytics()
    logger.info("Analytics data retrieved")