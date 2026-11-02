# Programming Guide

This guide explains the ideas and functions used by the Car Company Database program. It is written for a beginner and follows the program's actual design. The program stores records in MySQL; it does not save car data in a local project file.

**Project documents:** [README](README.md) · [CBSE project report](project_report.md)

## Contents

1. [Python](#python)
2. [SQL and MySQL](#sql-and-mysql)
3. [System Requirements](#system-requirements)
4. [Python and MySQL Connector](#python-and-mysql-connector)
5. [Database Tables](#database-tables)
6. [Program Functions](#program-functions)
7. [Imported Modules and Functions](#imported-modules-and-functions)
8. [Useful Built-in Functions and Methods](#useful-built-in-functions-and-methods)
9. [Test Helpers](#test-helpers)
10. [Reading the Code](#reading-the-code)
11. [Program Flow](#program-flow)
12. [Detailed Script Walkthrough](#detailed-script-walkthrough)
13. [Further Reading](#further-reading)

## Python

Python is a high-level, general-purpose programming language. It is designed to make program instructions readable. Python is interpreted: a Python interpreter reads and runs the program, so the programmer does not normally compile this project into a separate executable first.

### Salient features

- **Readable syntax:** indentation marks code blocks, and many operations use short, descriptive words.
- **Dynamically typed:** variables do not need a declared type, although values still have types such as string, integer, or decimal.
- **High-level:** the language handles many low-level details such as memory management.
- **Large standard library:** common tasks such as dates, terminal I/O, text handling, and tests are available without extra packages.
- **Cross-platform:** the same Python source can run on Windows, macOS, and Linux when compatible Python and packages are installed.
- **Extensible:** third-party packages can add capabilities, as MySQL Connector/Python does here.

### Applications

Python is used for automation and scripting, websites and web services, data analysis, scientific computing, education, testing, and database applications. This project uses it for a terminal interface, input checking, SQL execution, and error handling.

## SQL and MySQL

**SQL** means Structured Query Language. It is a language for defining and working with data in relational databases. The project uses SQL statements to create tables, insert and read records, update and delete records, join related rows, and calculate totals.

**MySQL** is a relational database management system (RDBMS). It runs as a database server, stores data in tables, and accepts SQL statements from client programs. In this project, Python is the client and MySQL Server stores the persistent car, production, and sales records.

### Salient features of MySQL

- Stores structured data in tables made of columns and rows.
- Uses primary keys to identify rows and foreign keys to maintain relationships.
- Supports multiple clients connecting to a server.
- Supports transactions; this application enables autocommit, so each successful data-changing statement is committed immediately.
- Supports SQL queries, indexes, constraints, and grouped calculations.
- Keeps data after the Python program exits; records are not held only in the program's memory.

### Applications

MySQL is commonly used for websites, business information systems, inventory, customer records, reporting, and other applications that need shared, persistent relational data. This school project uses it to demonstrate tables, keys, CRUD operations, joins, and aggregate totals.

### SQL ideas used here

- `CREATE DATABASE` creates the selected database.
- `CREATE TABLE` defines a table and its columns.
- `PRIMARY KEY` uniquely identifies each row.
- `AUTO_INCREMENT` asks MySQL to generate the next integer ID.
- `NOT NULL` requires a value.
- `UNIQUE` prevents duplicate model names.
- `FOREIGN KEY` requires a related car to exist.
- `INSERT`, `SELECT`, `UPDATE`, and `DELETE` add, read, change, and remove rows.
- `WHERE` limits which row an update or delete affects.
- `JOIN` combines related rows from two tables.
- `SUM` adds quantities, and `GROUP BY` calculates one sum per car.

A MySQL-specific part of this project is `AUTO_INCREMENT`. The connector's `%s` placeholders are also driver syntax for safely supplying values; they are not Python string interpolation.

## System Requirements

### Required software

- **Python:** The source uses Python 3.8 or newer syntax. Choose a MySQL Connector/Python release that supports your installed Python version; connector releases can have different minimum versions.
- **MySQL Server:** MySQL 8.0 or a compatible MySQL server, installed locally or reachable over a network.
- **Python package:** `mysql-connector-python`, installed from `requirements.txt`.
- **Terminal:** Windows Terminal/PowerShell, Command Prompt, macOS Terminal, or a Linux terminal.

The program uses only the Python standard library in addition to `mysql-connector-python`. `unittest` is part of Python and is not installed from `requirements.txt`.

### Required access and resources

- A MySQL account that can create the selected database and create tables in it. The program creates the database and tables when missing.
- A keyboard and terminal to use the menu.
- Internet access is needed to download the project or install the connector, but not for normal use when the project and MySQL server are available locally.
- Enough disk space for Python, MySQL Server if installed locally, and the database records. The project itself is small.

No specific processor, memory size, display resolution, or terminal-window dimensions are required for this small text-based program.

### Install and run

From the project directory, install the one external dependency and start the application:

```sh
python -m pip install -r requirements.txt
python car_company.py
```

On systems where the Python 3 command is named `python3`, use `python3` in both commands. The database server must be running and reachable before starting the app. The download instructions are in [README.md](README.md#download-to-desktop).

## Python and MySQL Connector

MySQL Connector/Python is the driver that lets a Python program communicate with a MySQL Server. Install it with:

```sh
python -m pip install mysql-connector-python
```

This project keeps that dependency in `requirements.txt` so the full project setup is repeatable:

```sh
python -m pip install -r requirements.txt
```

### Connection sequence in this program

1. `connect_to_database()` asks for the server host, username, password, and database name.
2. It validates the database name because it must be inserted into a SQL statement as an identifier.
3. `mysql.connector.connect(**settings)` opens a connection to the server without selecting a database.
4. A cursor runs `CREATE DATABASE IF NOT EXISTS` for the chosen name.
5. The first cursor and server connection are closed.
6. A second connection is opened with the selected database.
7. `create_tables()` creates missing tables and adds missing columns to older tables without deleting rows, then calls `commit()`.
8. Operations create cursors, execute SQL, fetch results where needed, and close cursors. The connection uses autocommit, so successful data-changing statements are committed immediately. The code still calls `commit()` after changes and attempts `rollback()` on errors, but rollback cannot undo a statement that has already been committed.
9. `main()` closes the database connection when the program exits.

The password is read with `getpass`, so normal terminal input does not echo it. The program does not save credentials to a local configuration file. Do not put a real password into source code or commit it to the repository.

### Parameterized values

For inserted, changed, and deleted values, the program uses `%s` placeholders and passes the values separately:

```python
cursor.execute(
    "INSERT INTO cars "
    "(model, price, manufacturer, model_year, color, is_electric) "
    "VALUES (%s, %s, %s, %s, %s, %s)",
    (model, price, manufacturer, model_year, color, is_electric),
)
```

This is safer and more reliable than building a SQL command by joining user text into it. SQL table and column names cannot be supplied as ordinary value placeholders; the program uses fixed table/column names from its `RECORDS` dictionary for those queries.

## Database Tables

The program creates three tables. The `cars` table is the parent. Each production or sales row belongs to one car through `car_id`. At startup, missing columns are added to older tables with defaults, so existing records are preserved.

```text
cars (one) ------ (many) production
cars (one) ------ (many) sales
```

The following is the standard tabular layout returned by MySQL's `DESCRIBE` command for the definitions in `create_tables()`. `Default` cells with no displayed value are blank. MySQL versions can format output differently, so run the commands below to see the exact output from your own server.

### `cars`

Command: `DESCRIBE cars;`

```text
+--------------+-----------------------+------+-----+---------+----------------+
| Field        | Type                  | Null | Key | Default | Extra          |
+--------------+-----------------------+------+-----+---------+----------------+
| car_id       | int                   | NO   | PRI | NULL    | auto_increment |
| model        | varchar(50)           | NO   | UNI | NULL    |                |
| price        | decimal(10,2)         | NO   |     | NULL    |                |
| manufacturer | varchar(50)           | NO   |     | Unknown |                |
| model_year   | smallint unsigned     | NO   |     | 2000    |                |
| color        | varchar(30)           | NO   |     | Unknown |                |
| is_electric  | tinyint(1)             | NO   |     | 0       |                |
+--------------+-----------------------+------+-----+---------+----------------+
```

- `car_id` is the primary key and is generated by MySQL.
- `model` is required and unique, so two cars cannot have the same model name.
- `price` is required and stores up to eight digits before and two digits after the decimal point.
- `manufacturer` and `color` are required text fields.
- `model_year` is stored as an unsigned small integer, and `is_electric` is stored as a Boolean.

### `production`

Command: `DESCRIBE production;`

```text
+-----------------+-------------------+------+-----+---------+----------------+
| Field           | Type              | Null | Key | Default | Extra          |
+-----------------+-------------------+------+-----+---------+----------------+
| production_id   | int               | NO   | PRI | NULL    | auto_increment |
| car_id          | int               | NO   | MUL | NULL    |                |
| production_date | date              | NO   |     | NULL    |                |
| quantity        | int               | NO   |     | NULL    |                |
| shift           | varchar(20)       | NO   |     | Day     |                |
| quality_checked | tinyint(1)        | NO   |     | 0       |                |
+-----------------+-------------------+------+-----+---------+----------------+
```

- `production_id` is the generated primary key for a production entry.
- `car_id` is a foreign key to `cars.car_id`. MySQL commonly displays its index as `MUL` because multiple production rows can refer to the same car.
- `production_date` stores the date of the entry.
- `quantity` stores the number made in this entry.
- `shift` records the production shift, and `quality_checked` records whether quality checks passed.

### `sales`

Command: `DESCRIBE sales;`

```text
+-----------------+------------------------+------+-----+---------+----------------+
| Field           | Type                   | Null | Key | Default | Extra          |
+-----------------+------------------------+------+-----+---------+----------------+
| sale_id         | int                    | NO   | PRI | NULL    | auto_increment |
| car_id          | int                    | NO   | MUL | NULL    |                |
| sale_date       | date                   | NO   |     | NULL    |                |
| quantity        | int                    | NO   |     | NULL    |                |
| sales_channel   | varchar(30)            | NO   |     | Other   |                |
| payment_method  | varchar(20)            | NO   |     | Other   |                |
| warranty_months | smallint unsigned      | NO   |     | 0       |                |
+-----------------+------------------------+------+-----+---------+----------------+
```

- `sale_id` is the generated primary key for a sales entry.
- `car_id` is a foreign key to `cars.car_id`.
- `sale_date` stores the date of the entry.
- `quantity` stores the number sold in this entry.
- `sales_channel` and `payment_method` store sale details; `warranty_months` stores the warranty length.

### Check the live table descriptions

After connecting to MySQL and selecting the project database, run:

```sql
USE car_company;
DESCRIBE cars;
DESCRIBE production;
DESCRIBE sales;
```

The foreign keys prevent inserting production or sales for a car that does not exist. They also prevent deleting a car while related rows remain. Delete the related rows first if removing that car is intended.

## Program Functions

These are the functions defined in `car_company.py`, grouped by what the program does.

### How the Python file is organized

- [Module description](car_company.py#L1) states the program's purpose, dependencies, and startup behavior.
- [Imports](car_company.py#L21) bring in date and decimal handling, password input, operating-system and terminal helpers, text formatting, and the MySQL connector. Only `mysql-connector-python` is an external package.
- [`DATABASE_DEFAULT`, `RECORDS`, `CAR_COLUMNS`, and `RECORD_COLUMNS`](car_company.py#L34) hold shared configuration. `RECORDS` maps supported record types to ID/date columns and display names; the column maps define extra fields and their migration defaults. SQL identifiers come only from these fixed mappings.
- The remainder of the file is arranged into terminal helpers, database setup, input validation, car operations, production/sales operations, summary reporting, and menu flow.

### Important Python constructs

- **Tuples and unpacking:** [`RECORDS`](car_company.py#L38) stores each record type as a tuple. Functions unpack a tuple into named fields, for example `id_column, date_column, title = RECORDS[table]`. This keeps the production and sales workflows shared without duplicating whole functions.
- **Dictionaries:** `settings` in [`connect_to_database()`](car_company.py#L201) holds connection options by name. `produced` and `sold` in [`show_summary()`](car_company.py#L815) map car IDs to totals, allowing `.get(car_id, 0)` to provide a missing total as zero.
- **Generator expressions:** expressions such as `(car[0] for car in cars)` pass car IDs to [`read_existing_id()`](car_company.py#L426) without creating another list.
- **F-strings:** prompts, headings, and SQL statements use f-strings to insert values into text. In SQL, user data still goes through connector placeholders; only fixed identifiers selected from `RECORDS` are put into the SQL text.
- **`try`, `except`, and `finally`:** `try` contains an operation that may fail, `except` handles a known error, and `finally` runs cleanup such as closing a cursor regardless of success or failure.
- **The `__main__` guard:** the final [`if __name__ == "__main__"` block](car_company.py#L997) starts `main()` only when this file is run directly. Importing the module from tests defines its functions without opening the menu.

### Source-code map

These are sections of one Python file, not separate modules. Use the linked definition for the exact location of each function.

| Source section | Purpose |
| --- | --- |
| [Imports and shared settings](car_company.py#L34) | Dependencies, default database name, and production/sales configuration. |
| [Terminal helpers](car_company.py#L65) | Screen clearing, headings, and the pause prompt. |
| [Database setup](car_company.py#L201) | Connection prompts, database creation, and table definitions. |
| [Input validation](car_company.py#L304) | Integer ranges, text lengths, yes/no values, price, model, ID, and date checks. |
| [Car operations](car_company.py#L486) | Select, display, add, update, and delete cars. |
| [Production and sales operations](car_company.py#L624) | Joined record display and shared record CRUD. |
| [Summary report](car_company.py#L799) | Group totals and the cars-left calculation. |
| [Menu and startup flow](car_company.py#L847) | Section menus, main menu, cleanup, and direct execution. |

### Data passed between functions

The MySQL connector returns rows as tuples. A car row has the shape `(car_id, model, price, manufacturer, model_year, color, is_electric)`. A production row also includes `shift` and `quality_checked`; a sales row also includes `sales_channel`, `payment_method`, and `warranty_months`. Functions unpack these tuples into names so each printed field is clear. The menu functions pass the database `connection` to operation functions; the connection is shared for the whole run, while each query creates and closes its own cursor.

### Terminal and connection

- **[`clear_screen()`](car_company.py#L65)** checks `stdin` and `stdout` with `isatty()`. It runs `cls` on Windows or `clear` elsewhere only for an interactive terminal; redirected output is left untouched.
- **[`print_heading(title)`](car_company.py#L71)** prints a centered title inside a compact terminal-width-aware frame.
- **[`read_input(message, separator=False)`](car_company.py#L81)** gives prompts a consistent `>` marker and optionally adds an underscore divider before menu choices.
- **[`print_table(headers, rows, max_widths=None, alignments=None)`](car_company.py#L124)** aligns and truncates columns to keep lists readable in narrower terminals.
- **[`pause_for_menu()`](car_company.py#L186)** waits for Enter after an action so its output is not immediately replaced by the next menu.
- **[`connect_to_database()`](car_company.py#L201)** asks for host, user, password, and database. It accepts the documented defaults, validates the database identifier against letters, digits, and underscores, opens a server connection to create the database if needed, closes that temporary connection, then returns a connection scoped to the chosen database. The MySQL account therefore needs database/table creation permission.
- **[`create_tables(connection)`](car_company.py#L245)** issues three `CREATE TABLE IF NOT EXISTS` statements, adds missing columns to pre-existing tables using defaults, applies key constraints, commits, and closes its cursor even if an error occurs. This migration preserves existing rows. MySQL implicitly commits DDL such as `CREATE TABLE` and `ALTER TABLE`; a later rollback cannot undo a schema change already applied.

The schema is described field-by-field in [Database Tables](#database-tables). The `cars` table is created first because `production.car_id` and `sales.car_id` refer to its primary key.

### Input checking and errors

- **[`read_positive_integer(message)`](car_company.py#L304)** loops until the input is a positive integer no larger than the signed MySQL `INT` maximum. Its digit-count check rejects excessively long input before integer conversion.
- **[`read_integer_range(message, minimum, maximum)`](car_company.py#L317)** validates unsigned small-integer fields such as model year and warranty months.
- **[`read_text(message, field_name, max_length)`](car_company.py#L328)** trims values and enforces the length of the corresponding `VARCHAR` field.
- **[`read_yes_no(message)`](car_company.py#L339)** accepts an explicit yes/no response for Boolean values.
- **[`read_price(message)`](car_company.py#L350)** parses input with `Decimal`, rejects non-finite and non-positive values, checks the maximum `DECIMAL(10,2)` value, and rejects more than two fractional digits.
- **[`read_model(message)`](car_company.py#L376)** trims surrounding whitespace and accepts only names from 1 to 50 characters, matching `VARCHAR(50)`.
- **[`read_existing_id(message, valid_ids)`](car_company.py#L426)** converts the displayed IDs to strings and accepts only an exact listed value. This prevents selecting an ID that was not offered in the current list.
- **[`read_date(message, default_today=False)`](car_company.py#L436)** accepts exact ISO `YYYY-MM-DD` calendar dates from MySQL's `1000-01-01` through `9999-12-31`. Future dates are valid for planning; new-entry prompts identify whether the value is a production or sale date, and an empty value defaults to today.
- Car model years accept 1886 through two years ahead of the current year, avoiding nonsensical year values while allowing near-future models.
- **[`show_error_details(error)`](car_company.py#L457)** converts an exception to text, detects the terminal width with an 80-column fallback, and wraps the message for display.
- **[`confirm_delete()`](car_company.py#L587)** normalizes the response to lowercase, repeats until the user enters `y` or `n`, and returns a Boolean confirmation.

### Car operations

- **[`fetch_cars(connection)`](car_company.py#L486)** runs the ordered `SELECT` for all car fields, returns all fetched rows, and closes the cursor in `finally`.
- **[`show_cars(connection)`](car_company.py#L499)** prints a heading and either an empty-state message or each returned car. It also returns the rows so callers can restrict ID input to visible cars.
- **[`add_car(connection)`](car_company.py#L529)** collects validated model, price, manufacturer, year, color, and electric status, inserts them with `%s` placeholders, and commits. A connector error is displayed and triggers rollback; the cursor is always closed.
- **[`update_car(connection)`](car_company.py#L550)** displays cars, validates the selected car ID, gathers replacement values for every car field, and updates the row selected by its primary key. A zero `rowcount` triggers a `SELECT` check so an unchanged car is not reported as missing.
- **[`delete_car(connection)`](car_company.py#L598)** displays cars, validates the ID, asks for confirmation, then deletes by primary key. A foreign-key error prevents removal if production or sales rows still refer to the car.

The car operations do not manually generate IDs. MySQL's `AUTO_INCREMENT` supplies them. A model duplicate is rejected by the database's `UNIQUE` rule, and the operation catches the connector error, rolls back, and displays its details.

### Production and sales operations

- **[`show_records(connection, table)`](car_company.py#L624)** uses the selected fixed `RECORDS` entry to choose table/column names, joins records to `cars` for readable model names, orders by record ID, prints the rows, and returns them for later ID validation.
- **[`add_record(connection, table)`](car_company.py#L686)** requires at least one car, accepts only a displayed car ID, reads a valid date, quantity, and table-specific extra values, then inserts the row. User values are bound separately from the SQL text.
- **[`update_record(connection, table)`](car_company.py#L722)** requires an existing record, validates both the record ID and replacement car ID, gathers date, quantity, and all extra values, then updates the selected record. A zero `rowcount` is checked for an unchanged existing row before reporting it missing.
- **[`delete_record(connection, table)`](car_company.py#L774)** requires an existing record and explicit confirmation before deleting by its record ID.
- **[`get_totals(connection, table, as_of=None)`](car_company.py#L799)** runs `SUM(quantity)` with `GROUP BY car_id`, filters out records after the supplied date, and converts the returned `(car_id, total)` pairs into a dictionary for quick lookups. The summary captures the date once so production and sales use the same cutoff.

The `table` argument to these shared operations must be one of the fixed `RECORDS` keys; it is not free-form user input. This is important because table and column names are interpolated into the SQL statement, while actual user values use placeholders.

This is the program's CRUD pattern: create with `INSERT`, read with `SELECT`,
edit with `UPDATE`, and remove with `DELETE`. Updates and deletes include a
`WHERE` condition on the selected primary-key ID. Connector `rowcount` reports
changed rows in the default configuration, not necessarily every matched row;
the update-result helper checks whether the row still exists when no values
changed. SQL identifiers come from fixed internal configuration, while user
values are passed as parameters.

### Summary and application flow

- **[`show_summary(connection)`](car_company.py#L815)** loads cars and production/sales totals independently, substitutes zero for a missing total, calculates `produced - sold`, and aligns the output columns. Future-dated records are excluded from the current totals; long labels are shortened for display only and negative totals remain visible.
- **[`manage_cars(connection)`](car_company.py#L847)** redraws the car menu, maps choices 1-4 to view/add/update/delete, pauses after an action, and returns to the main menu on 0.
- **[`manage_records(connection, table)`](car_company.py#L873)** uses the selected record type's display name, handles the same CRUD choices for production or sales, and returns on 0.
- **[`main()`](car_company.py#L922)** connects and initializes tables, displays the main menu, routes choices to the correct manager or summary, handles connector and keyboard/EOF errors, rolls back a failed menu operation, and closes the connection in `finally`.

`main()` has two error-handling phases. During startup it catches connection, schema, and user-interruption errors before entering the menu. During normal menu use it catches connector errors, attempts a rollback, and returns to the menu if the connection is still usable. The outer `finally` closes an open connection on normal exit or interruption.

### Tests for the code paths

The test module is [tests/test_car_company.py](tests/test_car_company.py). It
covers input validation, typed-field add/update/display operations, schema
migration, commit and rollback failures, summary date filtering and layout,
terminal output sanitization, and startup cleanup. Tests use fake database
objects and do not replace a live MySQL smoke test.

## Imported Modules and Functions

This section explains every imported module and imported API used by `car_company.py`.

| Import | Use in this program |
| --- | --- |
| [`datetime.date`](car_company.py) | Creates and validates calendar dates; `today()`, `fromisoformat()`, and `isoformat()` are used. |
| [`decimal.Decimal`](car_company.py) | Parses and compares prices without binary floating-point rounding. |
| [`decimal.InvalidOperation`](car_company.py) | Exception caught when price text is not a valid decimal. |
| [`getpass.getpass`](car_company.py) | Reads the MySQL password without echoing the typed characters. |
| [`os.name`](car_company.py) | Identifies the operating system (`nt` for Windows). |
| [`os.system(command)`](car_company.py) | Runs the terminal clear command (`cls` or `clear`). |
| [`re.fullmatch(pattern, text)`](car_company.py) | Checks that the complete database name contains only allowed letters, digits, or underscores. |
| [`shutil.get_terminal_size(fallback)`](car_company.py) | Gets terminal width for formatting database error messages; uses the fallback if size detection fails. |
| [`sys.stdin` and `sys.stdout`](car_company.py) | Refer to standard input and output; their `isatty()` methods identify interactive terminals. |
| [`textwrap.fill(text, width)`](car_company.py) | Wraps long error text to a selected width. |
| `unicodedata.east_asian_width(character)` and `unicodedata.combining(character)` | Help estimate terminal-cell widths for Unicode text when formatting tables. |
| [`mysql.connector.connect(**settings)`](car_company.py) | Opens a MySQL connection using the supplied host, user, password, and optional database. |
| [`mysql.connector.Error`](car_company.py#L32) | Base exception used to catch connector and database errors. |

`Decimal.is_finite()` and `Decimal.as_tuple()` are methods of the decimal value, not separately imported functions. They are used to reject non-finite prices and excess decimal places.

## Useful Built-in Functions and Methods

These functions are part of Python itself, so they do not appear in `requirements.txt`.

| Function or method | Purpose here |
| --- | --- |
| `input(prompt)` | Displays a prompt and reads a line from the terminal. |
| `print(value)` | Displays menu text, results, and error messages. |
| `int(text)` | Converts validated integer input to an integer value. |
| `str(value)` | Converts IDs to text for comparison with terminal input. |
| `len(value)` | Checks model-name length and sizes heading dividers. |
| `max(a, b)` | Keeps error wrapping at a minimum width. |
| `dict(rows)` | Builds the car-ID-to-total mapping returned by `get_totals()`. |
| `text.strip()` | Removes whitespace around typed values. |
| `text.lower()` | Normalizes a yes/no answer to lowercase. |
| `try` / `except` / `finally` | Handles invalid input and database errors while ensuring cursors are closed. |

MySQL Connector/Python also supplies the following objects and methods used in the code: `connection.cursor()` creates a cursor; `cursor.execute()` sends SQL to the server; `cursor.fetchall()` returns query rows; `cursor.rowcount` reports affected rows for updates and deletes; `connection.commit()` finalizes a transaction when one is active; `connection.rollback()` attempts to cancel the current transaction; `cursor.close()` and `connection.close()` release resources; and `connection.is_connected()` checks whether the connection is still open.

The application sets `connection.autocommit = True`. That means each successful
data-changing SQL statement is committed by MySQL without waiting for a later
`commit()` call. The calls to `commit()` remain as explicit markers in the
operation code and are useful if the connection's transaction settings are
changed later. Since each add, update, or delete uses one data-changing
statement, a failed statement does not leave a partial row update to undo.
`rollback()` is still attempted when a connector error occurs; it cannot undo
a statement that MySQL already committed.

### Test helpers

The automated tests use only Python's standard library in addition to the application:

| Import or API | Use in `tests/test_car_company.py` |
| --- | --- |
| `contextlib.redirect_stdout(stream)` | Captures printed output so tests can check the summary and messages. |
| `decimal.Decimal` | Supplies a precise example price to the fake database cursor. |
| `io.StringIO()` | Acts as an in-memory stream for captured output and fake terminal input/output. |
| `unittest.TestCase` | Provides test methods and assertion functions. |
| `unittest.main()` | Runs the tests when the test file is launched directly. |
| `unittest.mock.patch()` | Temporarily replaces input, terminal streams, and database functions during a test. |
| `car_company` | Imports the functions under test; the import does not start the menu because application startup is protected by the `__main__` check. |

The test fixtures' `execute()`, `fetchall()`, and `close()` methods imitate the cursor behavior used by the operations under test. They record SQL and parameters or return configured rows; they do not connect to a real database.

- [`FakeCursor`](tests/test_car_company.py#L12) returns configured sample rows for the cars and aggregate queries.
- [`FakeConnection`](tests/test_car_company.py#L45) creates those fake cursors and passes through production and sales totals.
- [`FakeStartupConnection`](tests/test_car_company.py#L54) records whether startup cleanup closed a connection.
- [`FakeTerminal`](tests/test_car_company.py#L62) behaves like an interactive terminal for screen-clear tests.

The test cases are grouped by behavior: [`InputValidationTests`](tests/test_car_company.py#L218), [`DeleteConfirmationTests`](tests/test_car_company.py#L537), [`SummaryTests`](tests/test_car_company.py#L581), and [`StartupCleanupTests`](tests/test_car_company.py#L778). Run them with `python -m unittest discover -s tests` from the project directory.

## Program Flow

This diagram follows the path through [`main()`](car_company.py#L922). A
section-menu action returns to that section's menu; choosing `0` returns to the
main menu. Database operation errors are reported and trigger a rollback
attempt; because autocommit is enabled, rollback cannot undo an already
committed statement.

```mermaid
flowchart TD
    Start([Run car_company.py]) --> Connect[Ask for MySQL settings]
    Connect --> CreateDB[Create database if missing]
    CreateDB --> OpenDB[Connect to selected database]
    OpenDB --> Tables[Create missing tables]
    CreateDB -. database error .-> StartupError[Show startup error]
    OpenDB -. connection error .-> StartupError
    Tables -. schema error .-> StartupError
    StartupError --> Close[Close connection if open]
    Tables --> MainMenu{Main menu choice}
    MainMenu -->|1| CarsMenu{Cars menu}
    MainMenu -->|2| ProductionMenu{Production menu}
    MainMenu -->|3| SalesMenu{Sales menu}
    MainMenu -->|4| Summary[Show production, sales, and cars left]
    MainMenu -->|0| Close
    CarsMenu -->|View, add, update, delete| CarAction[Run car operation]
    ProductionMenu -->|View, add, update, delete| ProductionAction[Run production operation]
    SalesMenu -->|View, add, update, delete| SalesAction[Run sales operation]
    CarAction -->|Return| CarsMenu
    ProductionAction -->|Return| ProductionMenu
    SalesAction -->|Return| SalesMenu
    CarsMenu -->|0| MainMenu
    ProductionMenu -->|0| MainMenu
    SalesMenu -->|0| MainMenu
    Summary --> MainMenu
    CarAction -. database error .-> Rollback[Rollback and show error]
    ProductionAction -. database error .-> Rollback
    SalesAction -. database error .-> Rollback
    Summary -. database error .-> Rollback
    Rollback -->|connection remains usable| MainMenu
    Rollback -->|connection lost| Close
    MainMenu -->|0| Close
    Close --> End([Exit])
```

1. `main()` opens a MySQL connection, creates missing tables, and adds missing columns to older tables using defaults.
2. The main menu routes to car management, production management, sales management, the summary, or exit.
3. Input helper functions validate values before database operations.
4. SQL statements run through connector cursors; values use `%s` placeholders.
5. Autocommit saves each successful data-changing statement immediately. Connector errors trigger a rollback attempt and a readable error message.
6. The summary adds production and sales dated through the current local date, then computes `Cars left = Produced - Sold` for each car. Future-dated plans are excluded.
7. On exit, `main()` closes the database connection.

## Reading the Code

### One database operation, step by step

[`add_car()`](car_company.py#L529) is a compact example of the program's usual database pattern:

1. Call [`read_model()`](car_company.py#L376) and [`read_price()`](car_company.py#L350) so values match the table's column rules.
2. Create a cursor with `connection.cursor()`. A cursor sends SQL and reads query results for one connection.
3. Call `cursor.execute(sql, values)`. The SQL contains `%s` markers and the values are passed as a tuple, keeping data separate from SQL syntax.
4. The connection uses autocommit, so MySQL saves the successful insert immediately; the code also calls `connection.commit()` explicitly.
5. If the connector raises `Error`, call `connection.rollback()` and show an explanation. With autocommit enabled, rollback cannot undo a statement that MySQL has already committed.
6. Close the cursor in `finally`, which runs whether the operation succeeds or fails.

Read operations such as [`fetch_cars()`](car_company.py#L486) follow the same cursor/cleanup pattern but call `fetchall()` and do not commit because they do not change data. [`create_tables()`](car_company.py#L245) is different only in that it executes several schema statements before one commit.

MySQL treats many DDL statements, including `CREATE DATABASE` and `CREATE TABLE`, as implicit-commit operations. The program still calls `commit()` after creating tables, but a later rollback cannot undo a table that MySQL has already created. For normal `INSERT`, `UPDATE`, and `DELETE` operations, autocommit saves each successful statement immediately; the explicit `commit()` calls do not create a larger transaction around multiple statements.

### How menu choices reach operations

[`main()`](car_company.py#L922) reads a choice and routes to the car manager, production manager, sales manager, summary, or exit. [`manage_cars()`](car_company.py#L847) uses a dictionary from menu numbers to functions, while [`manage_records()`](car_company.py#L873) uses a short `if`/`elif` chain for the shared production and sales actions. Both section menus clear the screen before drawing the next menu and pause after actions so the result remains visible. Option `0` returns to the previous menu; it does not delete data.

### Why the summary runs separate queries

[`get_totals()`](car_company.py#L799) runs a grouped total for one fixed table. [`show_summary()`](car_company.py#L815) calls it once for production and once for sales, then joins those results in Python by `car_id`. Keeping the two aggregates separate avoids multiplying rows if one car has several production entries and several sales entries. For each car, the displayed result is:

```text
Cars left = total produced - total sold
```

This is a simple arithmetic summary, not an inventory rule: sales are not
blocked when they exceed production. Future-dated production and sales entries
are treated as plans and do not affect today's totals.

## Detailed Script Walkthrough

This chapter follows the actual order and responsibilities in
[`car_company.py`](car_company.py). It explains how values move from the
terminal to the database and back again. The earlier [Program Functions](#program-functions)
section is a quick reference; this chapter gives the longer explanation.

### 1. File header, imports, and shared configuration

The module docstring at the top describes what the application stores, what
package it needs, and how to run it. A docstring is a string placed at the
start of a module, class, or function to describe its purpose. Python does not
execute the docstring as a menu command.

The imports near the top group the external dependency and standard-library
tools used throughout the file:

| Import | Why this script needs it |
| --- | --- |
| `date` | Validates user-entered calendar dates and captures today's local date for defaults and summaries. |
| `Decimal`, `InvalidOperation` | Handles prices exactly and recognizes invalid decimal input. |
| `getpass` | Reads the database password without echoing its characters. |
| `os`, `sys` | Chooses the screen-clear command and detects whether input/output are interactive terminals. |
| `re` | Applies whole-string patterns to database names, dates, prices, and integer input. |
| `shutil` | Reads terminal dimensions for headings, prompts, tables, and error messages. |
| `textwrap` | Wraps long database error text. |
| `unicodedata` | Estimates the terminal-cell width of combining and East Asian characters. |
| `mysql.connector`, `Error` | Opens MySQL connections and identifies connector/database errors. |

The configuration values are deliberately near the top:

- `DATABASE_DEFAULT` is the database name suggested at startup. The user can
  accept it or enter a different safe identifier.
- `EARLIEST_MODEL_YEAR` is 1886, the lower bound used by the car-model-year
  prompt.
- `MODEL_YEAR_FUTURE_LIMIT` is two. The upper year bound is recalculated from
  the current year each time car details are collected.
- `RECORDS` is the allow-list for the production and sales tables. For each
  supported type it stores the primary-key column, date column, and readable
  title.
- `RECORD_DATE_LABELS` supplies a clear prompt label for each date column.
- `RECORD_COLUMNS` lists the extra operational columns and SQL definitions
  for production and sales.
- `CAR_COLUMNS` lists additional car columns used by the existing-database
  migration.

Keeping table and column names in fixed configuration is important. SQL
placeholders can bind values such as names, quantities, and dates, but they
cannot bind identifiers such as a table name. The program therefore accepts
only `production` and `sales` for shared record operations instead of putting
typed text into SQL identifiers.

### 2. Terminal helpers and screen-width calculations

The terminal-helper functions isolate display concerns from database logic.
That makes it easier to change the interface without rewriting every query.

#### Clearing and headings

[`clear_screen()`](car_company.py#L65) checks both `sys.stdin.isatty()` and
`sys.stdout.isatty()`. It only clears when the program is connected to an
interactive terminal. When output is redirected to a file or a test captures
it, the function does nothing so it does not erase useful output or invoke a
terminal command unexpectedly.

[`print_heading(title)`](car_company.py#L71) calculates a frame from the
available terminal width, shortens an overly long title, and centers the
remaining title. `shutil.get_terminal_size((80, 24))` supplies a fallback for
environments that cannot report their terminal dimensions. The result is a
small framed heading that is consistent across the connection screen, menus,
and record views.

[`read_input(message, separator=False)`](car_company.py#L81) puts `>` in front
of each visible prompt. When `separator=True`, it prints a short underscore
line before the prompt. Menu handlers use that option to visually separate
the list of choices from the input location. Other field prompts remain
compact, so a form does not fill the screen with dividers.

#### Safe, readable table cells

[`visible_text(value)`](car_company.py#L89) converts a value to text and
escapes non-printable characters. This matters even if input validation is in
place: old database rows may have been entered by an earlier program version
or another client. Escaping a terminal control character prevents stored text
from clearing the screen, moving the cursor, or changing terminal colors.

[`display_width(value)`](car_company.py#L97) estimates how many terminal cells
a string occupies. Most characters count as one cell; full-width East Asian
characters count as two, and combining marks add no additional cell. This is
more useful for table layout than `len()` alone, because string length counts
Unicode code points rather than visual terminal cells.

[`fit_cell(value, width)`](car_company.py#L107) leaves short text untouched and
shortens long text to the assigned cell width. It reserves room for an
ellipsis when the column is wide enough and does not split a wide character
across the boundary.

[`print_table(headers, rows, max_widths=None, alignments=None)`](car_company.py#L124)
is the shared list renderer:

1. It converts headers and row values to terminal-safe text.
2. It checks that every row has one cell per header.
3. If maximum widths or alignments are provided, it checks that their lengths
   match the number of columns and that their values are valid.
4. It measures the natural width of every column.
5. It applies optional per-column limits.
6. If the total is wider than the terminal, it repeatedly shrinks the
   currently widest column, while keeping at least one display cell.
7. It truncates each cell, adds alignment padding, prints the header,
   separator, and data rows.

The car list right-aligns numeric values such as IDs and prices, while the
summary right-aligns counts. The table helper is intentionally not a full
spreadsheet renderer: it does not wrap values to multiple lines; it keeps one
record on one terminal line and uses an ellipsis where necessary.

[`pause_for_menu()`](car_company.py#L186) waits for Enter after an operation.
It goes through `read_input()` too, so the pause prompt uses the same visual
marker. [`close_connection()`](car_company.py#L191) centralizes connection
cleanup and prints details if the connector reports an error while closing.

### 3. Opening the MySQL connection

[`connect_to_database()`](car_company.py#L201) is responsible for gathering
connection settings and returning a connection that selects the application
database.

#### Collecting and checking the database name

The host and username prompts have defaults. An empty response selects the
default; a non-empty response is passed to the connector. `getpass()` handles
the password separately so it is not shown as the user types. The password
is used only to connect and is not written to a file or displayed.

The database name is interpolated into a `CREATE DATABASE` statement because
MySQL does not permit a normal value placeholder in place of an identifier.
Before doing that, the program requires one to 64 ASCII letters, numbers, or
underscores. The name is enclosed in backticks in SQL. Both steps constrain
the identifier to a simple, predictable format.

#### Why there are two connections

The program first connects to the server without a database selected. It
creates the requested database with `CREATE DATABASE IF NOT EXISTS`, then
closes that temporary server connection. It next opens a second connection
with the database selected. This sequence allows first-time setup to create
the database before trying to use it.

The first cursor and first connection are cleaned up in `finally` blocks. A
`finally` block runs whether its `try` body succeeds or raises an exception.
The second connection has `autocommit` enabled; if enabling it fails, that
connection is closed and the original connector error is re-raised for
startup handling.

#### Connection errors

The connection helper does not pretend a failed connection succeeded. Errors
from MySQL Connector/Python bubble to `main()`, which shows the failure and
offers the user a concise reminder to check the settings, connector, and
permissions. The database password is not part of that displayed error
message.

### 4. Creating and upgrading the database schema

[`create_tables(connection)`](car_company.py#L245) creates the parent `cars`
table first, then the child tables that refer to cars:

1. **`cars`** has an auto-generated integer key, unique model name, decimal
   price, manufacturer, model year, color, and electric flag.
2. **`production`** has an auto-generated production ID, a car foreign key,
   date, quantity, shift, and quality-check flag.
3. **`sales`** has an auto-generated sale ID, a car foreign key, date,
   quantity, channel, payment method, and warranty duration.

`CREATE TABLE IF NOT EXISTS` makes a missing table but does not change a table
that already exists. The startup migration handles that case. For each known
table it runs `SHOW COLUMNS`, stores the existing field names in a set, and
adds only fields from the trusted internal column map that are not already
present. The defaults fill the new `NOT NULL` columns for old rows:

| Table | Added field | Existing-row default |
| --- | --- | --- |
| `cars` | `manufacturer` | `Unknown` |
| `cars` | `model_year` | `2000` |
| `cars` | `color` | `Unknown` |
| `cars` | `is_electric` | `FALSE` |
| `production` | `shift` | `Day` |
| `production` | `quality_checked` | `FALSE` |
| `sales` | `sales_channel` | `Other` |
| `sales` | `payment_method` | `Other` |
| `sales` | `warranty_months` | `0` |

The migration does not drop a table or delete an old row. The schema setup
ends with `connection.commit()` and closes its cursor even when a query
fails. MySQL may implicitly commit statements such as `CREATE TABLE` and
`ALTER TABLE`; if a later migration statement fails, a rollback cannot
guarantee that already-applied DDL is undone. On the next startup, the code
checks the actual columns again and can continue adding missing columns.

### 5. Validating values before they reach SQL

The input functions loop until the user supplies a valid value. They return
typed data (integer, `Decimal`, Boolean, or ISO date string) to the operation
function; they do not talk to MySQL themselves.

#### Whole-number inputs

[`read_positive_integer(message)`](car_company.py#L304) handles quantities
that map to signed MySQL `INT` fields. It first matches digits only, and limits
input to ten digits before calling `int()`. That avoids expensive or
version-limited integer conversion for an extremely long string. It then
checks the range from 1 to 2,147,483,647. Zero, negative signs, decimal
fractions, extra characters, and values beyond the database range are
rejected.

[`read_integer_range(message, minimum, maximum)`](car_company.py#L317) does
the same for non-negative numeric fields with a caller-provided range. The
model year starts at 1886 and ends at the current year plus two. Warranty
months may be zero, so that prompt uses 0 to 65,535 for an unsigned
`SMALLINT`.

#### Text and Boolean inputs

[`read_text(message, field_name, max_length)`](car_company.py#L328) strips
leading and trailing whitespace and accepts only non-empty printable text
that fits the target `VARCHAR`. The field name is included in the error
message to make the correction clear.

[`read_yes_no(message)`](car_company.py#L339) trims and lowercases the answer.
It accepts `y`, `yes`, `n`, and `no` and returns the actual Boolean `True` or
`False`. It does not store a string such as `"yes"` in the Boolean column.

#### Prices

[`read_price(message)`](car_company.py#L350) validates a price for
`DECIMAL(10, 2)`. It accepts ordinary decimal notation, rejects scientific
notation, checks for a positive value, limits the numeric value to
99,999,999.99, and rejects more than two fractional digits. The `Decimal`
type avoids binary floating-point rounding; for example, a decimal amount
remains an exact decimal instead of being approximated as a float.

The regular expression also limits the raw whole-number digit count before
constructing the `Decimal`. Leading zeros may make the text longer without
changing the numeric value, but the numeric maximum is still enforced. Invalid
input receives the same concise prompt again rather than causing the menu to
crash.

#### Dates

[`read_date(message, default_today=False)`](car_company.py#L436) first
requires the exact shape `YYYY-MM-DD`, then asks `date.fromisoformat()` to
check that it is a real calendar date. It rejects dates before MySQL's
`1000-01-01` limit. Python dates cannot exceed `9999-12-31`, which is also the
upper limit supported by the MySQL `DATE` field.

Future dates are intentionally accepted. This permits planned production or
sales records. Adding a record may use today's local date by pressing Enter;
updating a record requires an explicit date. The prompt says whether the
entered date is a production date or a sale date so the user knows which event
is being recorded.

### 6. Shared lookup and validation configuration

[`get_record_config(table)`](car_company.py#L403) is a boundary check for
functions that share behavior between production and sales. It returns the
trusted tuple from `RECORDS`, or raises `ValueError` if an unsupported table
name is passed. The supported identifier is thus chosen by code, not built
from arbitrary terminal input.

[`read_record_details(table)`](car_company.py#L410) gathers fields that differ
by record type:

- For production it asks for a shift and whether the record passed quality
  checks.
- For sales it asks for a sales channel, payment method, and warranty duration.

`read_car_details(is_update=False)` similarly groups all car fields into one
validated return tuple. On an update it prefixes prompts with “New” but uses
the same validators and ranges as the add operation. This reduces the chance
that adding and updating a car behave differently.

### 7. Error display, rollback, and resource cleanup

[`show_error_details(error)`](car_company.py#L457) converts exception text to
a printable form, then wraps it to the terminal width. It uses a fallback
width when the terminal size is unavailable.

[`report_database_error(connection, error, message)`](car_company.py#L464)
prints a user-facing explanation, shows the database error details, and tries
to roll back. If rollback itself fails, it reports that second error and
re-raises it. Re-raising prevents a failed rollback from looking like a
success to the caller.

[`close_cursor(cursor)`](car_company.py#L476) catches connector errors during
cursor cleanup and reports them. All database functions use it from
`finally`, so cursor cleanup is attempted after both successful and failed
queries. `close_connection()` applies a similar cleanup pattern to a database
connection.

There are two layers of database error handling:

1. A CRUD function handles a known connector error close to the failed
   operation. It shows a context-specific message, reports the connector
   details, attempts rollback, and closes its cursor.
2. `main()` is the outer safety net for connector errors from operations that
   only read data, including displaying a list or calculating the summary.
   If rollback fails at the menu level, the connection is considered unusable
   and the application leaves the loop.

Input validation errors are handled separately from connector errors. A
`ValueError` from an unexpected application argument is reported without
claiming MySQL caused it.

### 8. Car table operations

#### Reading and displaying cars

[`fetch_cars(connection)`](car_company.py#L486) executes a fixed `SELECT` for
all seven car fields, orders by `car_id`, fetches the complete result, and
returns the row tuples. It closes the cursor in `finally`. It does not print,
which lets callers reuse the rows for both display and ID choices.

[`show_cars(connection)`](car_company.py#L499) formats these rows into the
shared terminal table. It returns the original database rows after printing.
That return value is important: update, delete, and record-entry operations
use the IDs from the list just displayed. If there are no cars, it prints an
empty-state message and returns an empty list.

#### Adding a car

[`add_car(connection)`](car_company.py#L529) runs this sequence:

1. Collect a model, price, manufacturer, year, color, and electric flag.
2. Create a cursor.
3. Execute one `INSERT` with six `%s` placeholders.
4. Commit after success and print a confirmation.
5. On a connector error, report the duplicate-model possibility and database
   details, then attempt rollback.
6. Close the cursor regardless of the result.

MySQL generates `car_id`; the user does not choose it. The unique constraint
in the schema is the final authority for preventing duplicate model names.
This protects data even if another database client inserts a duplicate at
the same time.

#### Updating a car

[`update_car(connection)`](car_company.py#L550) first displays all cars. If no
car exists, it returns instead of asking the user for an impossible ID. It
then accepts only an ID from the displayed list, collects replacement values
for every editable car field, and updates the row selected by `car_id`.

The update helper is called after the update statement. A connector may
report `rowcount == 0` when the selected row exists but the submitted values
are identical to the stored values. [`report_update_result()`](car_company.py#L900)
therefore runs a parameterized existence query. It reports either “No changes
needed” or “No car found” rather than confusing the two cases.

#### Deleting a car

[`confirm_delete()`](car_company.py#L587) repeats until the user explicitly
answers yes or no. [`delete_car(connection)`](car_company.py#L598) will not
execute its `DELETE` until the user selects an ID and confirms. The foreign
keys prevent deletion if production or sales rows still point to the car.
That constraint protects referential integrity; the application reports the
failure instead of silently deleting related data.

### 9. Production and sales record operations

The production and sales functions share code because the workflows are
similar. The fixed record metadata supplies their differences:

| Detail | Production | Sales |
| --- | --- | --- |
| ID field | `production_id` | `sale_id` |
| Date field | `production_date` | `sale_date` |
| Extra values | `shift`, `quality_checked` | `sales_channel`, `payment_method`, `warranty_months` |

#### Viewing joined records

[`show_records(connection, table)`](car_company.py#L624) verifies the table
choice, then builds a `SELECT` from trusted table/column configuration. It
joins the selected record table to `cars`, allowing the terminal list to
show the car model next to the stored `car_id`. It orders results by the
record's own ID.

The query returns a tuple shaped like:

```text
(record_id, car_id, model, date, quantity, extra_field_1, ...)
```

The function converts Boolean extra fields to “Yes” or “No”, chooses short
table headers for the extra columns, prints the rows, and returns the raw
rows. It closes its cursor before doing terminal formatting.

#### Adding a record

[`add_record(connection, table)`](car_company.py#L686) first shows cars and
requires one to exist. It asks for a car ID from that list, the correctly
named record date, a positive quantity, and the extra values for the chosen
table. It then creates the column list, a matching count of placeholders, and
the value tuple.

For production, the insert shape is conceptually:

```sql
INSERT INTO production
    (car_id, production_date, quantity, shift, quality_checked)
VALUES (%s, %s, %s, %s, %s);
```

For sales, the configured table and field names differ, but each user value
is still passed separately from the SQL text. After successful execution it
commits and confirms the record; on connector errors it displays details,
attempts rollback, and closes the cursor.

#### Updating a record

[`update_record(connection, table)`](car_company.py#L722) lists the current
records first and returns if there are none. It then:

1. Validates the selected record ID against the displayed records.
2. Shows cars and validates the replacement car ID.
3. Reads a new date, positive quantity, and every table-specific extra field.
4. Builds assignments from the known date and extra-column names.
5. Executes one `UPDATE` whose `WHERE` uses the selected primary key.
6. Commits and distinguishes changed, unchanged, and missing records.

All replacement values are updated together. The record's primary key is not
changed. This avoids partial update paths where, for example, the date is
updated but the quantity is forgotten.

#### Deleting a record

[`delete_record(connection, table)`](car_company.py#L774) requires an existing
record, validates its ID, asks for confirmation, and deletes only the row
identified by the selected record ID. It commits and checks `rowcount` to
report whether the row was removed. It does not cascade-delete a car or rows
from the other record table.

### 10. Summary calculations and date cutoffs

[`get_totals(connection, table, as_of=None)`](car_company.py#L799) validates
the record table and uses its configured date column. If no cutoff date is
provided, it captures today's local date. It then runs a grouped query:

```sql
SELECT car_id, SUM(quantity)
FROM production
WHERE production_date <= %s
GROUP BY car_id;
```

The actual date is passed as a connector parameter, not inserted into the SQL
string. The result is converted to a dictionary like `{car_id: total}`. A car
without a matching row is absent from that dictionary.

[`show_summary(connection)`](car_company.py#L815) captures the local date once
and passes the same date to both production and sales queries. This avoids a
midnight boundary where the production query and sales query might otherwise
use different days. Future-dated entries are plans, so they do not count in
the current total. The report names its “through” date so the cutoff is
visible to the user.

For each car, missing totals are treated as zero:

```text
produced_count = production_total.get(car_id, 0)
sold_count = sales_total.get(car_id, 0)
cars_left = produced_count - sold_count
```

This calculation is not inventory enforcement. A sale can exceed production,
and the displayed remaining number can be negative. The program keeps that
value visible rather than silently clamping it to zero.

### 11. Menus, application startup, and shutdown

[`manage_cars(connection)`](car_company.py#L847) presents numbered options and
maps choices 1 through 4 to the view, add, update, and delete functions. A
dictionary holds those callable functions, so the choice lookup is short.
Choice 0 returns to the main menu. An invalid choice prints the allowed range
and leaves the stored data untouched.

[`manage_records(connection, table)`](car_company.py#L873) presents the same
actions for production or sales. It uses the configured title, but dispatches
the choice through a short conditional chain because each function needs the
selected table argument.

[`main()`](car_company.py#L922) owns the application lifetime:

1. Start with `connection = None`, so cleanup can test whether a connection
   was successfully created.
2. Connect and initialize the schema.
3. If startup fails, display the error, close any connection already opened,
   and return before the menu begins.
4. Repeatedly display the main menu and route the choice to the relevant
   manager, summary, or exit.
5. Handle database errors that escape a lower-level read operation. Attempt a
   rollback; if rollback fails, stop using the connection.
6. Treat `KeyboardInterrupt` and `EOFError` as a user exit, so Ctrl+C or
   closed input does not leave the menu loop stuck.
7. In `finally`, check whether the connection is still open and close it.

The `if __name__ == "__main__":` guard calls `main()` only when this file is
executed as a script. Importing `car_company` from `tests/test_car_company.py`
defines functions without prompting for a password or opening the menu.

### 12. A request traced through the program

Suppose the user adds a sale:

1. `main()` receives menu choice `3` and calls
   `manage_records(connection, "sales")`.
2. The sales menu receives choice `2` and calls `add_record(connection, "sales")`.
3. `add_record()` checks for existing cars by calling `show_cars()`.
4. The user enters a car ID. `read_existing_id()` accepts only an ID that
   appeared in the just-displayed list.
5. `read_date()` validates the sale date. Entering nothing on this add form
   selects today's date.
6. `read_positive_integer()` validates quantity; `read_record_details()`
   validates channel, payment method, and warranty months.
7. The function assembles trusted SQL identifiers and creates a tuple of
   values. For example, an input date is a value, not part of the SQL text.
8. `cursor.execute()` sends the parameterized insert to MySQL.
9. The operation reports success or handles a connector error. The cursor is
   closed either way.
10. The sales menu pauses so the result remains visible, then redraws itself.

This separation of responsibilities helps debugging: if a date is rejected,
inspect `read_date()`; if the insert fails after values pass validation,
inspect the SQL columns and schema; if the row is saved but not shown,
inspect `show_records()` and its join.

### 13. Reading the tests as executable documentation

The tests in `tests/test_car_company.py` do not require a live database. Fake
cursor and connection objects record SQL and parameters or return configured
rows. `unittest.mock.patch()` replaces terminal input or a function for one
test, and `redirect_stdout()` captures what the program prints.

The test groups cover different contracts:

| Test group | What it checks |
| --- | --- |
| `InputValidationTests` | Boundary values, malformed dates and prices, text validation, prompt formatting, and allowed record names. |
| `SchemaMigrationTests` | New fields are added to older table layouts without `DROP` statements. |
| `CarOperationTests` | Car output, inserts, production inserts, sales updates, record output, and database failure behavior. |
| `DeleteConfirmationTests` | Invalid responses repeat; yes and no are interpreted correctly. |
| `UpdateResultTests` | A changed row, unchanged existing row, and missing row produce different messages. |
| `SummaryTests` | Date cutoffs, totals, alignment, narrow terminals, text safety, and display edge cases. |
| `StartupCleanupTests` | A connection opened during startup is closed if initialization is interrupted. |

These are unit tests: they check the application's logic with controlled
objects. They cannot prove that a particular MySQL account has permissions,
that a remote server is reachable, or that a deployed MySQL version accepts
every DDL statement. A complete deployment check also needs a MySQL server and
should test creating a fresh database and migrating an older one.

### 14. Troubleshooting by layer

| Symptom | First place to check | Reason |
| --- | --- | --- |
| Connection refused or times out | Host, port configuration, server status, and network reachability | The connector cannot establish the initial server connection. |
| Access denied while creating the database | Account name/password and `CREATE DATABASE` permission | Startup creates the chosen database when it is missing. |
| Access denied during table setup | Permissions for `CREATE TABLE`, `ALTER TABLE`, and reading column metadata | Startup also upgrades old tables with added fields. |
| Input keeps asking again | Read the range or format printed under the field prompt | The validator is rejecting a value before SQL is executed. |
| Duplicate-model error | Check whether the model already exists | MySQL enforces the unique index even if input validation succeeds. |
| Cannot delete a car | View and delete its production and sales records first | The foreign keys prevent orphaned records. |
| Summary number seems too low | Check whether some activity dates are in the future | Future-dated plans are intentionally excluded until their date. |
| Summary value is negative | Compare total recorded sales with production through the displayed date | The tool reports the arithmetic result and does not enforce stock limits. |
| List text contains visible escape sequences | Inspect legacy data for control characters | Terminal output escapes them so stored text cannot control the display. |
| Commit or rollback error appears | Check whether the server connection is still active | The program reports cleanup failures and avoids presenting rollback failure as success. |

When diagnosing a problem, note the exact prompt, menu selection, error
message, date entered, and whether the failure occurs on a fresh or previously
used database. Never include a real password in a bug report.

## Further Reading

- [Python documentation](https://docs.python.org/3/)
- [Python standard library](https://docs.python.org/3/library/)
- [MySQL Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)
- [MySQL Connector/Python Developer Guide](https://dev.mysql.com/doc/connector-python/en/)
- [Project README](README.md)
- [School project report](project_report.md)
