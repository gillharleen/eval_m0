import logging
import ingestor
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent 
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file_str = LOG_DIR / os.environ.get("LOG_FILE", "default.log")

log_level_str = os.environ.get("LOG_LEVEL", "WARNING").upper()

logging.basicConfig(filename=str(log_file_str),
                    format='%(asctime)s %(levelname)s [%(filename)s]: %(message)s',
                    filemode='a')

logger = logging.getLogger()
logger.setLevel(log_level_str)
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    logger.info("CSV processing started")
    ingestor.ingest_csv("src/input_files")
    logger.info("CSV processing finished")