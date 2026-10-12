# Ingestor file: reads csv files, checks rows, saves good rows in db.
import csv
from pathlib import Path
import logging
from pydantic import ValidationError
import database
import model

# logger for this file, writes to the same log file set in main
logger = logging.getLogger(__name__)

# read all csv files in folder and load good rows into db
def ingest_csv(folder_path):

    # empty table first so no duplicate rows
    database.clear_expenses()

    # go through each csv file
    for file in Path(folder_path).glob("*.csv"):
        logger.info("Reading file: %s", file.name)

        valid_rows = []
        total_rows = 0

        # utf-8-sig removes hidden BOM from excel files
        with file.open(newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)

            # start=2 because row 1 is header
            for row_number, row in enumerate(reader, start=2):
                total_rows += 1
                try:
                    # check the row with pydantic
                    expense = model.ExpenseRecord(**row)
                    valid_rows.append(expense)
                except ValidationError as error:
                    # log each error of the bad row and skip it
                    for e in error.errors():
                        field = e["loc"][0]
                        message = e["msg"] 
                        value = e["input"]

                        logger.error(
                            f"File: {file.name} | Row: {row_number} | Field: {field} | "
                            f"Error: {message} | Value: {value!r}"
                        )

        # insert all good rows of this file together
        if valid_rows:
            database.insert_data_to_db(valid_rows)

            logger.info(
                    "Inserted %d records out of %d from file %s",
                    len(valid_rows),
                    total_rows,
                    file.name,
                )
