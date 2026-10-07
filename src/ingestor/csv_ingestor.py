import csv
from pathlib import Path
import logging
from pydantic import ValidationError
from psycopg2.extras import execute_batch

import database
import model

logger = logging.getLogger(__name__)

def ingest_csv(folder_path):

    for file in Path(folder_path).glob("*.csv"):
        logger.info("Reading file: %s", file.name)

        valid_rows = []
        total_rows = 0

        with file.open(newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)

            for row_number, row in enumerate(reader, start=2):
                total_rows += 1
                try:
                    expense = model.ExpenseRecord(**row)
                    valid_rows.append(expense)
                except ValidationError as error:
                    for e in error.errors():
                        field = e["loc"][0]
                        message = e["msg"] 
                        value = e["input"]

                        logger.error(
                            f"File: {file.name} | Row: {row_number} | Field: {field} | "
                            f"Error: {message} | Value: {value!r}"
                        )

        if valid_rows:
                database.insert_data_to_db(valid_rows)

                logger.info(
                    "Inserted %d records out of %d from file %s",
                    len(valid_rows),
                    total_rows,
                    file.name,
                )
