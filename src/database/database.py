import os
import logging
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
BATCH_SIZE = 100

def get_connection():
    logger.info("Getting Database connection")
    return psycopg2.connect(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
    )


def insert_data_to_db(records):
    rows = [
        (r.expense_name, r.expense_amount, r.category, r.date, r.payment_method, r.description)
        for r in records
    ]

    connection = get_connection()
    logger.info("Inserting %d rows into table", len(records))
    with connection:
        with connection.cursor() as cursor:
            execute_values(
                cursor,
                "INSERT INTO expenses (expense_name, expense_amount, category, date, payment_method, description) "
                "VALUES %s",
                rows,
                page_size=BATCH_SIZE
            )
    connection.close()
    logger.info('Database connection closed')