# Database file: connects to postgres, inserts rows, runs report queries.
import os
import logging
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# load db details from .env
load_dotenv()

# logger for this file, writes to the same log file set in main
logger = logging.getLogger(__name__)

# rows sent in one insert
BATCH_SIZE = 100

# connect to postgres using .env values
def get_connection():
    return psycopg2.connect(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
    )

# delete all rows before new load, so no duplicates
def clear_expenses():
    logger.info('Empty the expenses table before a fresh load, so rows are not duplicated.')
    connection = get_connection()
     # commits if ok, rolls back if error
    with connection:
        with connection.cursor() as cursor:
            # remove all rows and reset id to 1
            cursor.execute("TRUNCATE TABLE expenses RESTART IDENTITY;")
    connection.close()
    logger.info("Expenses table cleared before loading")

# insert good rows into db in batches
def insert_data_to_db(records):
    # convert each record into a tuple
    rows = [
        (r.expense_name, r.expense_amount, r.category, r.date, r.payment_method, r.description)
        for r in records
    ]

    connection = get_connection()
    logger.info("Inserting %d rows into table", len(records))
    # all rows saved or none
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

# ---------- Report queries ----------

# runs a select query and returns rows, always closes connection
def __run_query(sql, params=None):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()


# Total spend and average spend
def total_and_average():
    return __run_query("""
        SELECT SUM(expense_amount), ROUND(AVG(expense_amount), 2)
        FROM expenses;
    """)

# total per category, highest first
def spending_by_category():
    return __run_query("""
        SELECT category, SUM(expense_amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC;
    """)

# total per month
def monthly_trends():
    return __run_query("""
        SELECT DATE_TRUNC('month', date)::date AS month, SUM(expense_amount) AS total
        FROM expenses
        GROUP BY month
        ORDER BY month;
    """)

# average per day
def daily_averages():
    return __run_query("""
        SELECT date, ROUND(AVG(expense_amount), 2) AS average
        FROM expenses
        GROUP BY date
        ORDER BY date;
    """)

# total between two dates
def spending_in_range(start_date, end_date):
    return __run_query("""
        SELECT SUM(expense_amount)
        FROM expenses
        WHERE date BETWEEN %s AND %s;
    """, (start_date, end_date))

