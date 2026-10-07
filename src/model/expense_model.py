from datetime import date, datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

class ExpenseRecord(BaseModel):
    model_config = {"str_strip_whitespace": True}

    expense_name: str = Field(min_length=1)
    expense_amount: float = Field(gt=0)
    category: str = Field(min_length=1)
    date: date
    payment_method: Literal["Cash", "UPI", "Card"]
    description: Optional[str] = None

    @field_validator("date", mode="before")
    def convert_date(cls, value):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except (ValueError, TypeError):
                pass
        raise ValueError("Use date format either 2026-10-01 or 01/10/2026")
    
    