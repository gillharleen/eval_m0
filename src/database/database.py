import os
import logging
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
BATCH_SIZE = 100

def get_connection():
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


def __run_query(sql, params=None):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()
    connection.close()


def total_and_average():
    return __run_query("""
        SELECT SUM(expense_amount), ROUND(AVG(expense_amount), 2)
        FROM expenses;
    """)


def spending_by_category():
    return __run_query("""
        SELECT category, SUM(expense_amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC;
    """)


def monthly_trends():
    return __run_query("""
        SELECT DATE_TRUNC('month', date)::date AS month, SUM(expense_amount) AS total
        FROM expenses
        GROUP BY month
        ORDER BY month;
    """)


def daily_averages():
    return __run_query("""
        SELECT date, ROUND(AVG(expense_amount), 2) AS average
        FROM expenses
        GROUP BY date
        ORDER BY date;
    """)


def spending_in_range(start_date, end_date):
    return __run_query("""
        SELECT SUM(expense_amount)
        FROM expenses
        WHERE date BETWEEN %s AND %s;
    """, (start_date, end_date))

