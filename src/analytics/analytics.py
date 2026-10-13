# Analytics file: runs report queries and prints them as tables.
from tabulate import tabulate
import database
import logging

# logger for this file, writes to the same log file set in main
logger = logging.getLogger(__name__)

# print title and rows as a table, numbers like 12,345.50
def print_table(title, rows, headers):
    table_str = tabulate(rows, headers=headers, tablefmt="rounded_outline", floatfmt=",.2f")
    analytics_output = f"\n{title}\n{table_str}"
    
    print(f"\n{analytics_output}")
    logger.info(f"{analytics_output}")

# print reports one by one 
def show_analytics():
    logger.info("Running total and average...")
    print_table("Summary", database.total_and_average(), ["Total", "Average"])

    logger.info("Running Spending by category...")
    print_table("Spending by category", database.spending_by_category(), ["Category", "Total"])

    logger.info("Running Monthly trends...")
    print_table("Monthly trends", database.monthly_trends(), ["Month", "Total"])

    logger.info("Running Daily averages...")
    print_table("Daily averages", database.daily_averages(), ["Date", "Average"])

    logger.info("Running Month's total spend...")
    october_spend = database.spending_in_range("2026-10-01", "2026-10-31")
    print_table("Total Spend of October 2026", october_spend, ["Amount"])