-- SQL file: creates the expenses table, runs when db container starts first time

-- create table only if it doesn't exist
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    expense_name VARCHAR(100) NOT NULL,
    expense_amount NUMERIC(12,2) NOT NULL
     CONSTRAINT chk_expense_amount CHECK (expense_amount > 0),
    category VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    payment_method VARCHAR(15) NOT NULL,
    description VARCHAR(255)
);

-- indexes for faster date and category queries
CREATE INDEX IF NOT EXISTS idx_expenses_date
ON expenses (date);

CREATE INDEX IF NOT EXISTS idx_expenses_category
ON expenses (category);