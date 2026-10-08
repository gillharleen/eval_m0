from datetime import date
import pytest
from pydantic import ValidationError
from model import ExpenseRecord

def test_valid_row():
    record = ExpenseRecord(
        expense_name="Lunch",
        expense_amount="250.50",
        category="Food",
        date="2026-10-01",
        payment_method="UPI",
    )
    assert record.expense_amount == 250.5
    assert record.date == date(2026, 10, 1)


def test_day_first_date():
    record = ExpenseRecord(
        expense_name="Cab",
        expense_amount=499,
        category="Travel",
        date="05/10/2026",
        payment_method="Card",
    )
    assert record.date == date(2026, 10, 5)


def test_negative_amount_is_rejected():
    with pytest.raises(ValidationError):
        ExpenseRecord(
            expense_name="Pen",
            expense_amount=-20,
            category="Stationery",
            date="2026-10-01",
            payment_method="Cash",
        )


def test_empty_category_is_rejected():
    with pytest.raises(ValidationError):
        ExpenseRecord(
            expense_name="Coffee",
            expense_amount=120,
            category="   ",
            date="2026-10-01",
            payment_method="UPI",
        )


def test_wrong_payment_method_is_rejected():
    with pytest.raises(ValidationError):
        ExpenseRecord(
            expense_name="Movie",
            expense_amount=500,
            category="Entertainment",
            date="2026-10-01",
            payment_method="Cheque",
        )