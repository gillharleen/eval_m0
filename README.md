# Expense CSV Ingestion & Analytics Pipeline

A Python command-line app that reads expense CSV files from a folder ([src/input_files](src/input_files)), validates every row with **Pydantic**, loads the valid rows into **PostgreSQL**, logs the invalid rows with the exact reason they failed, and prints a summary of spending analytics in the terminal. The whole stack runs with a single command 
```bash
docker compose up --build
```

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Flow Explanation](#data-flow-explanation)
3. [Git Workflow Explanation](#git-workflow-explanation)
4. [Setup and Execution Instructions](#setup-and-execution-instructions)
5. [Sample Analytics Outputs](#sample-analytics-outputs)
6. [Assumptions & Challenges](#assumptions--challenges)

---

## Architecture Overview

```mermaid
flowchart LR
    A[CSV Files in Folder] --> B[Python CLI]
    B --> C[Read CSV file and apply Pydantic Data Validation]
    C -->|Valid Records| D[(PostgreSQL Database)]
    C -->|Invalid Records| E[Log File / Error Output]
    D --> F[SQL Analytics Queries]
    F --> G[CLI Summary Output]
```

### Components

| Component | Responsibility |
|---|---|
| **CLI app** ([main.py](src/main.py)) | Configures file logging from `LOG_FILE` / `LOG_LEVEL`, then calls the [ingestor](src/ingestor/csv_ingestor.py) and the [analytics](src/analytics/analytics.py) module in order. |
| **Model** ([ExpenseRecord](src/model/expense_model.py)) | Defines what a valid expense is: required non-empty name and category, amount `> 0`, payment method one of `Cash` / `UPI` / `Card`, date in `YYYY-MM-DD` or `DD/MM/YYYY`, optional description. Whitespace is stripped automatically. |
| **Ingestor** ([csv_ingestor](src/ingestor/csv_ingestor.py)) | Loops over every `*.csv` file in the [input folder](src/input_files/), validates row by row, put valid records in a list, and logs each failed record with detailed error. |
| **Database layer** ([database](src/database/database.py)) | Ingestor calls database function to clears the table before a load, then call `insert_data_to_db` function to insert in batches with `execute_values` (batches of 100), and holds all analytics SQL. |
| **PostgreSQL** ([docker-compose](docker-compose.yml)) | Docker compose file has an image of postgresql database, it will store data in `expenses` table. `init.sql` runs automatically the first time the container starts. |
| **Analytics** ([analytics](src/analytics/analytics.py)) | Runs aggregation queries and prints them as formatted tables. |
| **pgAdmin** ([docker-compose](docker-compose.yml)) | Created this container to access Postgresql database through web UI on `http://localhost:5050`. |

### Project Structure

```
eval_m0/
├── src/
│   ├── main.py                  # Starting point: sets up logging, runs ingestion, then analytics
│   ├── model/
│   │   └── expense_model.py     # ExpenseRecord – Pydantic model with validation rules
│   ├── ingestor/
│   │   └── csv_ingestor.py      # Reads each CSV in the given folder, validates rows, sends valid rows to the DB
│   ├── database/
│   │   └── database.py          # Connection, truncate, batch insert, analytics SQL queries
│   ├── analytics/
│   │   └── analytics.py         # Call the database.py to Runs the queries and prints them as tables (tabulate)
│   └── input_files/             # Sample CSV input (*.csv)
├── tests/
│   └── test_expense_model.py    # pytest unit tests for the validation rules
├── init.sql                     # Script to be passed to docker-compose to create table schema and indexes
├── Dockerfile                   # Python application image configuration
├── docker-compose.yml           # db, app, pgadmin configuration
├── pyproject.toml / uv.lock     # Dependencies managed with uv
└── .env                         # Local config
```

---

## Data Flow Explanation

1. **Start-up.** `main.py` loads `.env`, creates the `logs/` folder and points the Python logger at `logs/<LOG_FILE>`.
2. **Database initialisation (first run only).** When the Postgres container starts with an empty volume, it runs `init.sql`, which creates the `expenses` table, its constraints and the two indexes.
3. **Clear the table.** `ingest_csv()` first calls `database.clear_expenses()`, which runs `TRUNCATE TABLE expenses RESTART IDENTITY;`. Every run is a fresh, full load, so running the app twice does not duplicate rows.
4. **Identify files to load.** All `*.csv` files in given `src/input_files/` folder are picked up, it has list of files to be processed one after the other.
5. **Read rows.** Each file is opened with `utf-8-sig` encoding (handles the invisible BOM that Excel adds) and read with `csv.DictReader`, so each row becomes a dictionary keyed by column name. Microsoft Excel adds a **Byte Order Mark (BOM)** —specifically the invisible sequence EF BB BF in hexadecimal (or \uFEFF)—when you save a spreadsheet using the CSV UTF-8 (Comma-delimited) format
6. **Validate each row.** The dictionary is passed to `ExpenseRecord(**row)`. Pydantic:
   - strips whitespace from strings,
   - converts `"250.50"` to a number and checks it is greater than 0,
   - checks `expense_name` and `category` are not empty,
   - parses the date from `2026-10-01` or `01/10/2026`,
   - checks `payment_method` is exactly `Cash`, `UPI` or `Card`.
7. **Route the result.**
   - **Valid →** added to a list for that file (each file being processed has its own fresh list).
   - **Invalid →** every failing field is written to the log as `CSV File Name | Row Number | Field/Column | Error | Value Provided`. Row numbers start at 2 because row 1 is the header.
8. **Store valid rows.** At the end of each file, the valid records are inserted in one transaction with `execute_values`. A summary such as `Inserted 2 records out of 4 from file expense1.csv` is logged.
9. **Run analytics.** `show_analytics()` runs five SQL queries against the loaded data:
   - total spend and average transaction (`SUM`, `AVG`)
   - spending by category (`GROUP BY category`)
   - monthly trends (`DATE_TRUNC('month', date)`)
   - daily averages (`GROUP BY date`)
   - total spend in a date range (`WHERE date BETWEEN %s AND %s`, parameterised)
10. **Print results.** Each result is printed to the terminal and log file as a table using `tabulate`.

---

## Git Workflow Explanation

The project follows a **feature branch workflow**. `main` always holds working, reviewed code. Every piece of work was done on its own branch and merged back through a pull request.

```mermaid
gitGraph
    commit id: "Initial commit"
    commit id: "gitignore, init.sql"
    branch feature/docker_compose
    commit id: "docker compose"
    checkout main
    merge feature/docker_compose id: "PR #1, #2"
    branch feature/ingest_csv
    commit id: ".env config + PG connection"
    checkout main
    merge feature/ingest_csv id: "PR #3"
    branch feature/validation
    commit id: "implemented CSV ingest"
    checkout main
    merge feature/validation id: "PR #4"
    branch feature/cli-analytics
    commit id: "analytical queries"
    checkout main
    merge feature/cli-analytics id: "PR #5"
    branch feature/docker-testing
    commit id: "Dockerfile + compose"
    commit id: "unit tests"
    checkout main
    merge feature/docker-testing id: "PR #6"
    branch feature/documentation
    commit id: "README docs"
    checkout main
    merge feature/documentation id: "PR #7"
```

### Process followed for each feature

```bash
# 1. Start from the latest main
git checkout main
git pull origin main

# 2. Create a feature branch on GitHub, then on local machine
git fetch
git switch feature/<name>

# 3. Commit small, focused changes
git add <files>
git commit -m "Short description of the change"

# 4. Push the branch to GitHub
git push -u origin feature/<name>

# 5. Open a pull request feature/<name> -> main on GitHub, review the diff, merge, then delete the feature branch

# 6. Update local main after the merge
git checkout main
git pull origin main
```

---

## Setup and Execution Instructions

### 1. Clone the repository

```bash
git clone https://github.com/gillharleen/eval_m0.git
cd eval_m0
```

### 2. Create the `.env` file

`.env` is not committed. Create it in the project root:

```env
# PostgreSQL
POSTGRES_USER=db_user
POSTGRES_PASSWORD=db_password
POSTGRES_DB=expenses_db
POSTGRES_HOST=localhost      # overridden to "db" inside Docker Compose
POSTGRES_PORT=5432           # port the app connects to
POSTGRES_INT_PORT=5432       # port Postgres listens on inside the container

# pgAdmin
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=pg_admin_password

# Logging
LOG_FILE=m0_expense_ingest.log
LOG_LEVEL=INFO
```

### Option A — Entire system runnable using one command

```bash
docker compose up --build
```

This will:
1. start PostgreSQL database and run `init.sql` on first start,
2. wait until the database is healthy,
3. build the app image and run `python src/main.py`,
4. start pgAdmin on <http://localhost:5050>.

The analytics tables appear in the terminal, prefixed with `app-1  |`. The `app` container exits after printing; `db` and `pgadmin` keep running. 

```bash
docker compose down        # stop containers
```

### Option B — Run the Python app locally (but database in Docker)

```bash
# Start only PostgreSQL and PgAdmin Containers
docker compose up -d db pgadmin

# Install dependencies and run the pipeline
uv sync
uv run src/main.py
```

### Run the tests

```bash
uv run pytest -v
```

```
tests/test_expense_model.py::test_valid_row PASSED                       [ 20%]
tests/test_expense_model.py::test_day_first_date PASSED                  [ 40%]
tests/test_expense_model.py::test_negative_amount_is_rejected PASSED     [ 60%]
tests/test_expense_model.py::test_empty_category_is_rejected PASSED      [ 80%]
tests/test_expense_model.py::test_wrong_payment_method_is_rejected PASSED [100%]

============================== 5 passed in 0.11s ===============================
```

[test_expense_model.py](tests/test_expense_model.py)

### Clean-slate verification

```bash
docker compose down
docker compose up --build
```

`down` removes the container, so `init.sql` runs again and the whole pipeline is tested from zero.

---

## Sample Analytics Outputs

Input: `src/input_files/*.csv`.

### CLI terminal output

```
Summary
╭─────────────────────┬──────────╮
│ Metric              │   Amount │
├─────────────────────┼──────────┤
│ Total spend         │ 1,499.00 │
│ Average transaction │   374.75 │
╰─────────────────────┴──────────╯

Spending by category
╭────────────┬─────────╮
│ Category   │   Total │
├────────────┼─────────┤
│ Travel     │  998.00 │
│ Food       │  501.00 │
╰────────────┴─────────╯

Monthly trends
╭────────────┬──────────╮
│ Month      │    Total │
├────────────┼──────────┤
│ 2026-10-01 │ 1,499.00 │
╰────────────┴──────────╯

Daily averages
╭────────────┬───────────╮
│ Date       │   Average │
├────────────┼───────────┤
│ 2026-10-01 │    250.50 │
│ 2026-10-05 │    499.00 │
╰────────────┴───────────╯

October 2026
╭─────────────┬──────────╮
│ Metric      │   Amount │
├─────────────┼──────────┤
│ Total spend │ 1,499.00 │
╰─────────────┴──────────╯
```

### Queries behind the output

| Report | SQL |
|---|---|
| Summary | `SELECT SUM(expense_amount), ROUND(AVG(expense_amount), 2) FROM expenses;` |
| Spending by category | `SELECT category, SUM(expense_amount) AS total FROM expenses GROUP BY category ORDER BY total DESC;` |
| Monthly trends | `SELECT DATE_TRUNC('month', date)::date AS month, SUM(expense_amount) AS total FROM expenses GROUP BY month ORDER BY month;` |
| Daily averages | `SELECT date, ROUND(AVG(expense_amount), 2) AS average FROM expenses GROUP BY date ORDER BY date;` |
| Date range total | `SELECT SUM(expense_amount) FROM expenses WHERE date BETWEEN %s AND %s;` |

---

## Assumptions & Challenges

### Assumptions

- **Fixed CSV header.** Every file has the columns `expense_name, expense_amount, category, date, payment_method, description`. The header names must match the model field names.
- **Two accepted date formats.** `YYYY-MM-DD` and `DD/MM/YYYY` (Indian day-first style). Anything else, such as `26-10-07`, is rejected rather than guessed.
- **Three payment methods.** Only `Cash`, `UPI` and `Card` are valid, and the match is case-sensitive.
- **Full refresh on every run.** The table is truncated before each load. The CSV folder is treated as the single source of truth, which keeps runs repeatable (running twice still gives 4 rows, not 8).
- **No de-duplication across files.** `expense1.csv` and `expense2.csv` contain the same valid rows, and both copies are loaded. That is why Food shows 501.00 (2 × 250.50). Identical rows in different files are treated as separate expenses.
- **Description is optional.** An empty description is allowed.

### Error handling decisions

| Situation | Decision | Reason |
|---|---|---|
| A row fails validation | Skip the row, log every failing field, continue | One typo shouldn't block the rest of the file |
| A row has several bad fields | Log all of them | The user can fix everything in one go |
| A file has no valid rows | Skip the insert for that file | Avoids an empty database call |
| Bad data reaches the database anyway | `CHECK` constraints reject it | Defence in depth |
| Database not ready yet in Docker | `depends_on: condition: service_healthy` | The app only starts once `pg_isready` succeeds |
