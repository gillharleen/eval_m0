from tabulate import tabulate
import database
import logging

logger = logging.getLogger(__name__)

def print_table(title, rows, headers):
    print(f"\n{title}")
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline", floatfmt=",.2f"))

def show_analytics():
    logger.info("Running total and average...")
    total, average = database.total_and_average()[0]
    print_table("Summary", [["Total spend", total], ["Average transaction", average]], ["Metric", "Amount"])

    logger.info("Running Spending by category...")
    print_table("Spending by category", database.spending_by_category(), ["Category", "Total"])

    logger.info("Running Monthly trends...")
    print_table("Monthly trends", database.monthly_trends(), ["Month", "Total"])

    logger.info("Running Daily averages...")
    print_table("Daily averages", database.daily_averages(), ["Date", "Average"])

    logger.info("Running Month's total spend...")
    month = database.spending_in_range("2026-10-01", "2026-10-31")[0][0]
    print_table("October 2026", [["Total spend", month]], ["Metric", "Amount"])