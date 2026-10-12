# Model file: checks each csv row before saving to db.
from datetime import date, datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

# checks one row of the csv, bad rows raise ValidationError
class ExpenseRecord(BaseModel):

    # remove extra spaces from text fields
    model_config = {"str_strip_whitespace": True}

    expense_name: str = Field(min_length=1) # cannot be empty
    expense_amount: float = Field(gt=0) # must be more than 0
    category: str = Field(min_length=1) # cannot be empty
    date: date                          # converted by convert_date below
    payment_method: Literal["Cash", "UPI", "Card"] # only these 3 allowed
    description: Optional[str] = None   # optional

    # runs before pydantic's own date check
    @field_validator("date", mode="before")
    def convert_date(cls, value):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                # try both date formats one by one
                return datetime.strptime(value, fmt).date()
            except (ValueError, TypeError):
                pass
        # no format matched
        raise ValueError("Use date format either 2026-10-01 or 01/10/2026")
    
    