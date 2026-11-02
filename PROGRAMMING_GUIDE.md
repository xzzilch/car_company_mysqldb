# Programming Guide

This guide explains how the Car Company Database works, from its MySQL tables
to the Python functions that read and change them. The program stores records
in MySQL rather than in a local project data file.

**Project documents:** [README](README.md) · [CBSE project report](project_report.md)

**Recommended reading path:** For a first read, follow **System Requirements →
Python and MySQL Connector →
Database Tables → Application Architecture → Program Flow → Three Design
Choices → Detailed Script Walkthrough**. This path introduces the data first,
then shows how the code uses it. Later function, data-contract, and
troubleshooting sections are look-up references; they repeat selected details
for quick access rather than describing extra runtime steps.

## Contents

### Background and setup

- [Python](#python)
- [SQL and MySQL](#sql-and-mysql)
- [System requirements](#system-requirements)
- [Python and MySQL Connector](#python-and-mysql-connector)
- [Database tables](#database-tables)

### Follow the application

- [Application architecture](#application-architecture)
- [Program flow](#program-flow)
- [Three design choices](#three-design-choices)
- [Detailed script walkthrough](#detailed-script-walkthrough)

### Look up details

- [Source-code map](#source-code-map)
- [Imported modules and functions](#imported-modules-and-functions)
- [Useful built-in functions and methods](#useful-built-in-functions-and-methods)
- [Test helpers](#test-helpers)
- [How to use source references](#how-to-use-the-source-references)
- [Function-by-function reference](#function-by-function-reference)
- [Data contracts and query shapes](#data-contracts-and-query-shapes)
- [End-to-end operations](#end-to-end-operations)
- [Reliability, errors, and edge cases](#reliability-errors-and-edge-cases)
- [How to extend the program](#how-to-extend-the-program)
- [Further reading](#further-reading)

## Python

Python is a high-level, general-purpose programming language. It is designed to make program instructions readable. Python is interpreted: a Python interpreter reads and runs the program, so the programmer does not normally compile this project into a separate executable first.

### Salient features

- **Readable syntax:** indentation marks code blocks, and many operations use short, descriptive words.
- **Dynamically typed:** variables do not need a declared type, although values still have types such as string, integer, or decimal.
- **High-level:** the language handles many low-level details such as memory management.
- **Large standard library:** common tasks such as dates, terminal I/O, text handling, and tests are available without extra packages.
- **Cross-platform:** the same Python source can run on Windows, macOS, and Linux when compatible Python and packages are installed.
- **Extensible:** third-party packages can add capabilities, as MySQL Connector/Python does here.

### Python in this project

The script uses Python to collect and validate terminal input, format results,
coordinate the menus, and call MySQL Connector/Python. Keeping those tasks in
separate functions makes the database behavior easier to read and test.

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

MySQL Connector/Python is the driver that lets a Python program communicate
with MySQL Server. It is the only external runtime dependency listed in
[`requirements.txt`](requirements.txt); use the [Install and run](#install-and-run)
instructions above rather than installing it a second time.

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

## Application Architecture

This is a map of the program's components, not another step-by-step
description. Use it to understand how responsibilities are divided; the next
chapters trace the runtime flow and then follow the source in order.

### How the Python file is organized

- [Module description](car_company.py#L1) states the program's purpose, dependencies, and startup behavior.
- [Imports](car_company.py#L23) bring in date and decimal handling, password input, operating-system and terminal helpers, text formatting, and the MySQL connector. Only `mysql-connector-python` is an external package.
- [`DATABASE_DEFAULT`, `RECORDS`, `CAR_COLUMNS`, and `RECORD_COLUMNS`](car_company.py#L36) hold shared configuration. `RECORDS` maps supported record types to ID/date columns and display names; the column maps define extra fields and their migration defaults. SQL identifiers come only from these fixed mappings.
- The remainder of the file is arranged into terminal helpers, database setup, input validation, car operations, production/sales operations, summary reporting, and menu flow.

### Important Python constructs

- **Tuples and unpacking:** [`RECORDS`](car_company.py#L40) stores each record type as a tuple. Functions unpack a tuple into named fields, for example `id_column, date_column, title = RECORDS[table]`. This keeps the production and sales workflows shared without duplicating whole functions.
- **Dictionaries:** `settings` in [`connect_to_database()`](car_company.py#L203) holds connection options by name. `produced` and `sold` in [`show_summary()`](car_company.py#L817) map car IDs to totals, allowing `.get(car_id, 0)` to provide a missing total as zero.
- **Generator expressions:** expressions such as `(car[0] for car in cars)` pass car IDs to [`read_existing_id()`](car_company.py#L428) without creating another list.
- **F-strings:** prompts, headings, and SQL statements use f-strings to insert values into text. In SQL, user data still goes through connector placeholders; only fixed identifiers selected from `RECORDS` are put into the SQL text.
- **`try`, `except`, and `finally`:** `try` contains an operation that may fail, `except` handles a known error, and `finally` runs cleanup such as closing a cursor regardless of success or failure.
- **The `__main__` guard:** the final [`if __name__ == "__main__"` block](car_company.py#L999) starts `main()` only when this file is run directly. Importing the module from tests defines its functions without opening the menu.

### Source-code map

These are sections of one Python file, not separate modules. Use the linked definition for the exact location of each function.

| Source section | Purpose |
| --- | --- |
| [Imports and shared settings](car_company.py#L36) | Dependencies, default database name, and production/sales configuration. |
| [Terminal helpers](car_company.py#L67) | Screen clearing, headings, and the pause prompt. |
| [Database setup](car_company.py#L203) | Connection prompts, database creation, and table definitions. |
| [Input validation](car_company.py#L306) | Integer ranges, text lengths, yes/no values, price, model, ID, and date checks. |
| [Car operations](car_company.py#L488) | Select, display, add, update, and delete cars. |
| [Production and sales operations](car_company.py#L626) | Joined record display and shared record CRUD. |
| [Summary report](car_company.py#L801) | Group totals and the cars-left calculation. |
| [Menu and startup flow](car_company.py#L849) | Section menus, main menu, cleanup, and direct execution. |

### Data passed between functions

The MySQL connector returns rows as tuples. A car row has the shape `(car_id, model, price, manufacturer, model_year, color, is_electric)`. A production row also includes `shift` and `quality_checked`; a sales row also includes `sales_channel`, `payment_method`, and `warranty_months`. Functions unpack these tuples into names so each printed field is clear. The menu functions pass the database `connection` to operation functions; the connection is shared for the whole run, while each query creates and closes its own cursor.

### Terminal and connection

- **[`clear_screen()`](car_company.py#L67)** checks `stdin` and `stdout` with `isatty()`. It runs `cls` on Windows or `clear` elsewhere only for an interactive terminal; redirected output is left untouched.
- **[`print_heading(title)`](car_company.py#L73)** prints a centered title inside a compact terminal-width-aware frame.
- **[`read_input(message, separator=False)`](car_company.py#L83)** gives prompts a consistent `>` marker and optionally adds an underscore divider before menu choices.
- **[`print_table(headers, rows, max_widths=None, alignments=None)`](car_company.py#L126)** aligns and truncates columns to keep lists readable in narrower terminals.
- **[`pause_for_menu()`](car_company.py#L188)** waits for Enter after an action so its output is not immediately replaced by the next menu.
- **[`connect_to_database()`](car_company.py#L203)** asks for host, user, password, and database. It accepts the documented defaults, validates the database identifier against letters, digits, and underscores, opens a server connection to create the database if needed, closes that temporary connection, then returns a connection scoped to the chosen database. The MySQL account therefore needs database/table creation permission.
- **[`create_tables(connection)`](car_company.py#L247)** issues three `CREATE TABLE IF NOT EXISTS` statements, adds missing columns to pre-existing tables using defaults, applies key constraints, commits, and closes its cursor even if an error occurs. This migration preserves existing rows. MySQL implicitly commits DDL such as `CREATE TABLE` and `ALTER TABLE`; a later rollback cannot undo a schema change already applied.

The schema is described field-by-field in [Database Tables](#database-tables). The `cars` table is created first because `production.car_id` and `sales.car_id` refer to its primary key.

### Input checking and errors

- **[`read_positive_integer(message)`](car_company.py#L306)** loops until the input is a positive integer no larger than the signed MySQL `INT` maximum. Its digit-count check rejects excessively long input before integer conversion.
- **[`read_integer_range(message, minimum, maximum)`](car_company.py#L319)** validates unsigned small-integer fields such as model year and warranty months.
- **[`read_text(message, field_name, max_length)`](car_company.py#L330)** trims values and enforces the length of the corresponding `VARCHAR` field.
- **[`read_yes_no(message)`](car_company.py#L341)** accepts an explicit yes/no response for Boolean values.
- **[`read_price(message)`](car_company.py#L352)** parses input with `Decimal`, rejects non-finite and non-positive values, checks the maximum `DECIMAL(10,2)` value, and rejects more than two fractional digits.
- **[`read_model(message)`](car_company.py#L378)** trims surrounding whitespace and accepts only names from 1 to 50 characters, matching `VARCHAR(50)`.
- **[`read_existing_id(message, valid_ids)`](car_company.py#L428)** converts the displayed IDs to strings and accepts only an exact listed value. This prevents selecting an ID that was not offered in the current list.
- **[`read_date(message, default_today=False)`](car_company.py#L438)** accepts exact ISO `YYYY-MM-DD` calendar dates from MySQL's `1000-01-01` through `9999-12-31`. Future dates are valid for planning; new-entry prompts identify whether the value is a production or sale date, and an empty value defaults to today.
- Car model years accept 1886 through two years ahead of the current year, avoiding nonsensical year values while allowing near-future models.
- **[`show_error_details(error)`](car_company.py#L459)** converts an exception to text, detects the terminal width with an 80-column fallback, and wraps the message for display.
- **[`confirm_delete()`](car_company.py#L589)** normalizes the response to lowercase, repeats until the user enters `y` or `n`, and returns a Boolean confirmation.

### Car operations

- **[`fetch_cars(connection)`](car_company.py#L488)** runs the ordered `SELECT` for all car fields, returns all fetched rows, and closes the cursor in `finally`.
- **[`show_cars(connection)`](car_company.py#L501)** prints a heading and either an empty-state message or each returned car. It also returns the rows so callers can restrict ID input to visible cars.
- **[`add_car(connection)`](car_company.py#L531)** collects validated model, price, manufacturer, year, color, and electric status, inserts them with `%s` placeholders, and commits. A connector error is displayed and triggers rollback; the cursor is always closed.
- **[`update_car(connection)`](car_company.py#L552)** displays cars, validates the selected car ID, gathers replacement values for every car field, and updates the row selected by its primary key. A zero `rowcount` triggers a `SELECT` check so an unchanged car is not reported as missing.
- **[`delete_car(connection)`](car_company.py#L600)** displays cars, validates the ID, asks for confirmation, then deletes by primary key. A foreign-key error prevents removal if production or sales rows still refer to the car.

The car operations do not manually generate IDs. MySQL's `AUTO_INCREMENT` supplies them. A model duplicate is rejected by the database's `UNIQUE` rule, and the operation catches the connector error, rolls back, and displays its details.

### Production and sales operations

- **[`show_records(connection, table)`](car_company.py#L626)** uses the selected fixed `RECORDS` entry to choose table/column names, joins records to `cars` for readable model names, orders by record ID, prints the rows, and returns them for later ID validation.
- **[`add_record(connection, table)`](car_company.py#L688)** requires at least one car, accepts only a displayed car ID, reads a valid date, quantity, and table-specific extra values, then inserts the row. User values are bound separately from the SQL text.
- **[`update_record(connection, table)`](car_company.py#L724)** requires an existing record, validates both the record ID and replacement car ID, gathers date, quantity, and all extra values, then updates the selected record. A zero `rowcount` is checked for an unchanged existing row before reporting it missing.
- **[`delete_record(connection, table)`](car_company.py#L776)** requires an existing record and explicit confirmation before deleting by its record ID.
- **[`get_totals(connection, table, as_of=None)`](car_company.py#L801)** runs `SUM(quantity)` with `GROUP BY car_id`, filters out records after the supplied date, and converts the returned `(car_id, total)` pairs into a dictionary for quick lookups. The summary captures the date once so production and sales use the same cutoff.

The `table` argument to these shared operations must be one of the fixed `RECORDS` keys; it is not free-form user input. This is important because table and column names are interpolated into the SQL statement, while actual user values use placeholders.

This is the program's CRUD pattern: create with `INSERT`, read with `SELECT`,
edit with `UPDATE`, and remove with `DELETE`. Updates and deletes include a
`WHERE` condition on the selected primary-key ID. Connector `rowcount` reports
changed rows in the default configuration, not necessarily every matched row;
the update-result helper checks whether the row still exists when no values
changed. SQL identifiers come from fixed internal configuration, while user
values are passed as parameters.

### Summary and application flow

- **[`show_summary(connection)`](car_company.py#L817)** loads cars and production/sales totals independently, substitutes zero for a missing total, calculates `produced - sold`, and aligns the output columns. Future-dated records are excluded from the current totals; long labels are shortened for display only and negative totals remain visible.
- **[`manage_cars(connection)`](car_company.py#L849)** redraws the car menu, maps choices 1-4 to view/add/update/delete, pauses after an action, and returns to the main menu on 0.
- **[`manage_records(connection, table)`](car_company.py#L875)** uses the selected record type's display name, handles the same CRUD choices for production or sales, and returns on 0.
- **[`main()`](car_company.py#L924)** connects and initializes tables, displays the main menu, routes choices to the correct manager or summary, handles connector and keyboard/EOF errors, rolls back a failed menu operation, and closes the connection in `finally`.

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
| [`mysql.connector.Error`](car_company.py#L34) | Base exception used to catch connector and database errors. |

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

This diagram follows the path through [`main()`](car_company.py#L924). A
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

## Three Design Choices

The flowchart above shows what happens. These short examples explain why
three parts are implemented the way they are before the longer source tour.

### One database operation, step by step

[`add_car()`](car_company.py#L531) is a compact example of the program's usual database pattern:

1. Call [`read_model()`](car_company.py#L378) and [`read_price()`](car_company.py#L352) so values match the table's column rules.
2. Create a cursor with `connection.cursor()`. A cursor sends SQL and reads query results for one connection.
3. Call `cursor.execute(sql, values)`. The SQL contains `%s` markers and the values are passed as a tuple, keeping data separate from SQL syntax.
4. The connection uses autocommit, so MySQL saves the successful insert immediately; the code also calls `connection.commit()` explicitly.
5. If the connector raises `Error`, call `connection.rollback()` and show an explanation. With autocommit enabled, rollback cannot undo a statement that MySQL has already committed.
6. Close the cursor in `finally`, which runs whether the operation succeeds or fails.

Read operations such as [`fetch_cars()`](car_company.py#L488) follow the same cursor/cleanup pattern but call `fetchall()` and do not commit because they do not change data. [`create_tables()`](car_company.py#L247) is different only in that it executes several schema statements before one commit.

MySQL treats many DDL statements, including `CREATE DATABASE` and `CREATE TABLE`, as implicit-commit operations. The program still calls `commit()` after creating tables, but a later rollback cannot undo a table that MySQL has already created. For normal `INSERT`, `UPDATE`, and `DELETE` operations, autocommit saves each successful statement immediately; the explicit `commit()` calls do not create a larger transaction around multiple statements.

### How menu choices reach operations

[`main()`](car_company.py#L924) reads a choice and routes to the car manager, production manager, sales manager, summary, or exit. [`manage_cars()`](car_company.py#L849) uses a dictionary from menu numbers to functions, while [`manage_records()`](car_company.py#L875) uses a short `if`/`elif` chain for the shared production and sales actions. Both section menus clear the screen before drawing the next menu and pause after actions so the result remains visible. Option `0` returns to the previous menu; it does not delete data.

### Why the summary runs separate queries

[`get_totals()`](car_company.py#L801) runs a grouped total for one fixed table. [`show_summary()`](car_company.py#L817) calls it once for production and once for sales, then joins those results in Python by `car_id`. Keeping the two aggregates separate avoids multiplying rows if one car has several production entries and several sales entries. For each car, the displayed result is:

```text
Cars left = total produced - total sold
```

This is a simple arithmetic summary, not an inventory rule: sales are not
blocked when they exceed production. Future-dated production and sales entries
are treated as plans and do not affect today's totals.

## Detailed Script Walkthrough

This chapter follows the actual order and responsibilities in
[`car_company.py`](car_company.py). Sections 1–11 form the main source tour:
they explain how values move from the terminal to the database and back.
The [Application Architecture](#application-architecture) section is a
component map; the later function and data-contract chapters are references,
not additional steps in program execution.

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

[`clear_screen()`](car_company.py#L67) checks both `sys.stdin.isatty()` and
`sys.stdout.isatty()`. It only clears when the program is connected to an
interactive terminal. When output is redirected to a file or a test captures
it, the function does nothing so it does not erase useful output or invoke a
terminal command unexpectedly.

[`print_heading(title)`](car_company.py#L73) calculates a frame from the
available terminal width, shortens an overly long title, and centers the
remaining title. `shutil.get_terminal_size((80, 24))` supplies a fallback for
environments that cannot report their terminal dimensions. The result is a
small framed heading that is consistent across the connection screen, menus,
and record views.

[`read_input(message, separator=False)`](car_company.py#L83) puts `>` in front
of each visible prompt. When `separator=True`, it prints a short underscore
line before the prompt. Menu handlers use that option to visually separate
the list of choices from the input location. Other field prompts remain
compact, so a form does not fill the screen with dividers.

#### Safe, readable table cells

[`visible_text(value)`](car_company.py#L91) converts a value to text and
escapes non-printable characters. This matters even if input validation is in
place: old database rows may have been entered by an earlier program version
or another client. Escaping a terminal control character prevents stored text
from clearing the screen, moving the cursor, or changing terminal colors.

[`display_width(value)`](car_company.py#L99) estimates how many terminal cells
a string occupies. Most characters count as one cell; full-width East Asian
characters count as two, and combining marks add no additional cell. This is
more useful for table layout than `len()` alone, because string length counts
Unicode code points rather than visual terminal cells.

[`fit_cell(value, width)`](car_company.py#L109) leaves short text untouched and
shortens long text to the assigned cell width. It reserves room for an
ellipsis when the column is wide enough and does not split a wide character
across the boundary.

[`print_table(headers, rows, max_widths=None, alignments=None)`](car_company.py#L126)
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

[`pause_for_menu()`](car_company.py#L188) waits for Enter after an operation.
It goes through `read_input()` too, so the pause prompt uses the same visual
marker. [`close_connection()`](car_company.py#L193) centralizes connection
cleanup and prints details if the connector reports an error while closing.

### 3. Opening the MySQL connection

[`connect_to_database()`](car_company.py#L203) is responsible for gathering
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

[`create_tables(connection)`](car_company.py#L247) creates the parent `cars`
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

[`read_positive_integer(message)`](car_company.py#L306) handles quantities
that map to signed MySQL `INT` fields. It first matches digits only, and limits
input to ten digits before calling `int()`. That avoids expensive or
version-limited integer conversion for an extremely long string. It then
checks the range from 1 to 2,147,483,647. Zero, negative signs, decimal
fractions, extra characters, and values beyond the database range are
rejected.

[`read_integer_range(message, minimum, maximum)`](car_company.py#L319) does
the same for non-negative numeric fields with a caller-provided range. The
model year starts at 1886 and ends at the current year plus two. Warranty
months may be zero, so that prompt uses 0 to 65,535 for an unsigned
`SMALLINT`.

#### Text and Boolean inputs

[`read_text(message, field_name, max_length)`](car_company.py#L330) strips
leading and trailing whitespace and accepts only non-empty printable text
that fits the target `VARCHAR`. The field name is included in the error
message to make the correction clear.

[`read_yes_no(message)`](car_company.py#L341) trims and lowercases the answer.
It accepts `y`, `yes`, `n`, and `no` and returns the actual Boolean `True` or
`False`. It does not store a string such as `"yes"` in the Boolean column.

#### Prices

[`read_price(message)`](car_company.py#L352) validates a price for
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

[`read_date(message, default_today=False)`](car_company.py#L438) first
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

[`get_record_config(table)`](car_company.py#L405) is a boundary check for
functions that share behavior between production and sales. It returns the
trusted tuple from `RECORDS`, or raises `ValueError` if an unsupported table
name is passed. The supported identifier is thus chosen by code, not built
from arbitrary terminal input.

[`read_record_details(table)`](car_company.py#L412) gathers fields that differ
by record type:

- For production it asks for a shift and whether the record passed quality
  checks.
- For sales it asks for a sales channel, payment method, and warranty duration.

`read_car_details(is_update=False)` similarly groups all car fields into one
validated return tuple. On an update it prefixes prompts with “New” but uses
the same validators and ranges as the add operation. This reduces the chance
that adding and updating a car behave differently.

### 7. Error display, rollback, and resource cleanup

[`show_error_details(error)`](car_company.py#L459) converts exception text to
a printable form, then wraps it to the terminal width. It uses a fallback
width when the terminal size is unavailable.

[`report_database_error(connection, error, message)`](car_company.py#L466)
prints a user-facing explanation, shows the database error details, and tries
to roll back. If rollback itself fails, it reports that second error and
re-raises it. Re-raising prevents a failed rollback from looking like a
success to the caller.

[`close_cursor(cursor)`](car_company.py#L478) catches connector errors during
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

[`fetch_cars(connection)`](car_company.py#L488) executes a fixed `SELECT` for
all seven car fields, orders by `car_id`, fetches the complete result, and
returns the row tuples. It closes the cursor in `finally`. It does not print,
which lets callers reuse the rows for both display and ID choices.

[`show_cars(connection)`](car_company.py#L501) formats these rows into the
shared terminal table. It returns the original database rows after printing.
That return value is important: update, delete, and record-entry operations
use the IDs from the list just displayed. If there are no cars, it prints an
empty-state message and returns an empty list.

#### Adding a car

[`add_car(connection)`](car_company.py#L531) runs this sequence:

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

[`update_car(connection)`](car_company.py#L552) first displays all cars. If no
car exists, it returns instead of asking the user for an impossible ID. It
then accepts only an ID from the displayed list, collects replacement values
for every editable car field, and updates the row selected by `car_id`.

The update helper is called after the update statement. A connector may
report `rowcount == 0` when the selected row exists but the submitted values
are identical to the stored values. [`report_update_result()`](car_company.py#L902)
therefore runs a parameterized existence query. It reports either “No changes
needed” or “No car found” rather than confusing the two cases.

#### Deleting a car

[`confirm_delete()`](car_company.py#L589) repeats until the user explicitly
answers yes or no. [`delete_car(connection)`](car_company.py#L600) will not
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

[`show_records(connection, table)`](car_company.py#L626) verifies the table
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

[`add_record(connection, table)`](car_company.py#L688) first shows cars and
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

[`update_record(connection, table)`](car_company.py#L724) lists the current
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

[`delete_record(connection, table)`](car_company.py#L776) requires an existing
record, validates its ID, asks for confirmation, and deletes only the row
identified by the selected record ID. It commits and checks `rowcount` to
report whether the row was removed. It does not cascade-delete a car or rows
from the other record table.

### 10. Summary calculations and date cutoffs

[`get_totals(connection, table, as_of=None)`](car_company.py#L801) validates
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

[`show_summary(connection)`](car_company.py#L817) captures the local date once
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

[`manage_cars(connection)`](car_company.py#L849) presents numbered options and
maps choices 1 through 4 to the view, add, update, and delete functions. A
dictionary holds those callable functions, so the choice lookup is short.
Choice 0 returns to the main menu. An invalid choice prints the allowed range
and leaves the stored data untouched.

[`manage_records(connection, table)`](car_company.py#L875) presents the same
actions for production or sales. It uses the configured title, but dispatches
the choice through a short conditional chain because each function needs the
selected table argument.

[`main()`](car_company.py#L924) owns the application lifetime:

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

### Worked example: adding a sale

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

### Tests as executable documentation

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

### Troubleshooting by layer

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

## How to Use the Source References

This reference complements the earlier conceptual walkthrough. It is
organized around the actual definition order in [car_company.py](car_company.py),
so a reader can move from a section of this guide to the corresponding code
without guessing. Each function link points to its definition line. In a
local editor, use the link to open the file near that definition; on GitHub,
the `#L<number>` fragment highlights the source line.

The source line numbers are a navigation aid, not part of the Python API.
When the program changes, a new function may shift later line numbers. The
function name remains the reliable identifier: use the link, then search for
the definition if a source link no longer lands exactly on it.

### A quick route through the file

| If you want to understand... | Start here | Then follow |
| --- | --- | --- |
| How a value is displayed | [`print_table()`](car_company.py#L126) | [`visible_text()`](car_company.py#L91), [`display_width()`](car_company.py#L99), [`fit_cell()`](car_company.py#L109) |
| Why input is accepted or rejected | The matching `read_*()` validator | [`read_car_details()`](car_company.py#L387) or [`read_record_details()`](car_company.py#L412) |
| How the database is prepared | [`connect_to_database()`](car_company.py#L203) | [`create_tables()`](car_company.py#L247) |
| How a car is saved | [`add_car()`](car_company.py#L531) | [`read_car_details()`](car_company.py#L387), then `cars` in [Database Tables](#database-tables) |
| How a production or sales row is saved | [`add_record()`](car_company.py#L688) | [`get_record_config()`](car_company.py#L405), [`read_record_details()`](car_company.py#L412) |
| Why an update says “No changes needed” | [`report_update_result()`](car_company.py#L902) | [`update_car()`](car_company.py#L552) or [`update_record()`](car_company.py#L724) |
| How summary totals are calculated | [`show_summary()`](car_company.py#L817) | [`get_totals()`](car_company.py#L801) |
| How the program exits cleanly | [`main()`](car_company.py#L924) | [`close_connection()`](car_company.py#L193) and the [main guard](car_company.py#L999) |

### What a function reference describes

For each function, distinguish four things:

1. **Inputs:** arguments passed by the caller, plus any terminal values the
   function asks the user to enter.
2. **Return value:** data returned to the caller. A function that only prints
   has an implicit return value of `None`.
3. **Side effects:** visible output, SQL execution, changes to stored rows,
   or resource cleanup.
4. **Failure behavior:** invalid user input is generally retried by a
   validator; database failures are handled by the operation or by `main()`.

This distinction explains why a query helper such as [`fetch_cars()`](car_company.py#L488)
returns rows but does not print, while [`show_cars()`](car_company.py#L501)
prints those rows and also returns them for a later ID choice.

## Function-by-Function Reference

Use this chapter as a lookup when you need one function's responsibility or
contract. The continuous explanation is in the
[Detailed Script Walkthrough](#detailed-script-walkthrough); the table below
is not a second execution path.

### Module description, imports, and configuration

The file begins with a module docstring, imports, and shared constants rather
than a class hierarchy. The project is intentionally a small procedural
application: each function has one narrow responsibility, while the
connection object is passed explicitly to database operations.

| Source reference | Responsibility and behavior |
| --- | --- |
| [Module docstring](car_company.py#L1) | States the project's purpose, dependencies, setup behavior, and run command. It is documentation, not executable menu logic. |
| [Imports](car_company.py#L23) | Load Python's date, decimal, password, OS, regex, terminal, text, and Unicode utilities plus the MySQL connector. Only the connector is an installed project dependency. |
| [`DATABASE_DEFAULT`](car_company.py#L36) | Supplies the suggested schema name when the user presses Enter at startup. |
| [`EARLIEST_MODEL_YEAR`](car_company.py#L37) and [`MODEL_YEAR_FUTURE_LIMIT`](car_company.py#L38) | Define the lower model-year bound and how far into the future a model year may be entered. The upper limit is based on the current year. |
| [`RECORDS`](car_company.py#L40) | Maps the two accepted record kinds to their key column, date column, and display title. It acts as a small allow-list for shared SQL operations. |
| [`RECORD_DATE_LABELS`](car_company.py#L44) | Keeps the production-date and sale-date prompts explicit instead of showing the underlying column identifiers. |
| [`RECORD_COLUMNS`](car_company.py#L48) | Specifies extra production/sales fields and their DDL definitions, including defaults needed when migrating an existing table. |
| [`CAR_COLUMNS`](car_company.py#L59) | Specifies additional car fields and their migration definitions. `create_tables()` uses this mapping when it finds an older schema. |

The configuration dictionaries are important because SQL placeholders are
for values, not table or column names. A supported record name is selected
from [`RECORDS`](car_company.py#L40), and the program interpolates only those
known identifiers into a query. User-entered model names, dates, prices,
quantities, and other values remain query parameters.

### Terminal helpers

Terminal helpers keep formatting rules out of database functions. They do
not open a database cursor or alter stored information.

#### Screen, prompt, and cleanup helpers

| Function | Contract |
| --- | --- |
| [`clear_screen()`](car_company.py#L67) | Checks whether both input and output are interactive terminals. It runs the operating-system clear command only in that case, so redirected output and automated test captures are not erased. It returns nothing. |
| [`print_heading(title)`](car_company.py#L73) | Chooses a width from the terminal size, with a fallback, shortens a title if needed, and prints a centered framed heading. The width is based on Python string length; table rendering has a more Unicode-aware calculation. |
| [`read_input(message, separator=False)`](car_company.py#L83) | Prints a consistent `>` prompt and returns the raw input line. When `separator` is true, it prints a bounded underscore divider before reading a menu choice. Validation belongs to the caller, not this helper. |
| [`pause_for_menu()`](car_company.py#L188) | Uses `read_input()` to wait for Enter so the latest action result stays visible until the user continues. |
| [`close_connection(connection)`](car_company.py#L193) | Attempts to close a connection and reports a connector error. It deliberately does not pretend the connection was closed if the connector raises an error. |

#### Making database text safe to show

[`visible_text(value)`](car_company.py#L91) converts a value to a string and
escapes non-printable characters. This matters when displaying old or
externally modified database rows: a stored newline, tab, or terminal control
character should not unexpectedly move the cursor or create fake rows.
Escaping is for terminal display only; it does not modify the database value.

[`display_width(value)`](car_company.py#L99) approximates the number of
terminal cells used by text. Combining marks take no additional cell, and
full-width or wide East Asian characters count as two. This is more useful
for terminal alignment than `len(value)`, which counts Python code points
rather than visible cells. Terminal emulators can differ, so this is a
practical estimate rather than a complete grapheme-rendering engine.

[`fit_cell(value, width)`](car_company.py#L109) keeps a value within a
requested cell width. If text is too long, it reserves room for an ellipsis
when the column can fit one, then copies whole characters until the remaining
width is used. It avoids splitting a wide character in half. It does not
wrap text: one database record remains one terminal row.

[`print_table(headers, rows, max_widths=None, alignments=None)`](car_company.py#L126)
is the table renderer:

1. It converts headers and cells with `visible_text()`.
2. It rejects rows whose cell count does not match the header count.
3. It validates optional width and alignment specifications before printing.
4. It calculates each natural width using `display_width()`, then applies any
   caller-provided maximum widths.
5. If the combined table is wider than the terminal, it repeatedly shrinks
   the currently widest column without reducing a column below one cell.
6. It applies `fit_cell()` and pads each value on the left or right according
   to the requested alignment.
7. It prints a header, separator, and data rows.

An empty `headers` sequence is a valid no-op. A mismatched row or invalid
formatting option raises `ValueError`, making a caller's layout bug explicit
instead of silently misaligning data. The helper does not print a special
empty-state message; its caller decides whether an empty query result should
say “No cars found” or “No records found.”

### Database setup

#### [`connect_to_database()`](car_company.py#L203)

This function is the entry point from terminal settings to a live connection.
It reads the host, user, hidden password, and database name. Empty host, user,
or database input selects the documented default. The database identifier
must match a limited ASCII pattern and length because it is embedded as an
identifier in `CREATE DATABASE`; the password and other values are never
printed or written to a project config file.

There are two connections for a reason. The first is made without a selected
database so the program can issue `CREATE DATABASE IF NOT EXISTS`. The first
cursor and connection are closed in `finally` blocks. A second connection is
then opened with the chosen database, and `autocommit` is enabled. If setting
that property raises a connector error, the partially initialized connection
is closed before the error propagates.

This function returns the database connection. It does not create the tables;
startup calls [`create_tables()`](car_company.py#L247) immediately afterward.
Connector errors are allowed to reach [`main()`](car_company.py#L924), where
startup failures are displayed and the application exits before presenting
the menu.

#### [`create_tables(connection)`](car_company.py#L247)

This function creates the parent `cars` table before `production` and
`sales`, because both child tables reference `cars.car_id`. Each definition
declares types, nullability, defaults, generated keys, uniqueness, and
foreign-key relationships. `CREATE TABLE IF NOT EXISTS` makes a missing
table, but intentionally does not rewrite a table that already exists.

The second part is a small additive migration. For each known table, it reads
the field names with `SHOW COLUMNS`, compares them with the relevant internal
column map, and issues `ALTER TABLE ... ADD COLUMN` for missing fields only.
This keeps old rows and supplies defaults for newly added required columns.
It is not a general schema-versioning engine: it adds configured fields, but
does not rename columns, alter an existing column's type, or remove fields.

The function uses one cursor and closes it in `finally`. MySQL DDL can
implicitly commit, so neither the explicit final `commit()` nor a later
rollback makes the group of schema statements fully atomic. If a migration
stops partway through, the next startup inspects the actual columns and can
continue with what is still missing.

### Input validators and field collection

The `read_*()` validators own the retry loop: they read input, test its
shape and bounds, print a correction when needed, and return a typed value
only when it is acceptable. They do not execute SQL. The CRUD operation that
calls a validator therefore receives either a valid value or a user
interruption such as `EOFError` or `KeyboardInterrupt`.

| Function | Accepted result | Main checks |
| --- | --- | --- |
| [`read_positive_integer(message)`](car_company.py#L306) | Python `int` | ASCII digits only, at most ten input digits, and range 1 through signed MySQL `INT` maximum. |
| [`read_integer_range(message, minimum, maximum)`](car_company.py#L319) | Python `int` | ASCII digits only, bounded input length, then inclusive caller-supplied minimum and maximum. |
| [`read_text(message, field_name, max_length)`](car_company.py#L330) | Trimmed `str` | Not empty, printable, and no longer than the target column. |
| [`read_yes_no(message)`](car_company.py#L341) | Python `bool` | Case-insensitive `y`, `yes`, `n`, or `no`; other text is retried. |
| [`read_price(message)`](car_company.py#L352) | `Decimal` | Ordinary decimal syntax, finite positive value, no more than two fractional places, and no more than `99,999,999.99`. |
| [`read_model(message)`](car_company.py#L378) | Trimmed `str` | Non-empty, printable model name of at most 50 characters. |
| [`read_existing_id(message, valid_ids)`](car_company.py#L428) | Python `int` | Exact textual match against IDs provided by the caller; arbitrary IDs are not accepted. |
| [`read_date(message, default_today=False)`](car_company.py#L438) | ISO date `str` | Exact `YYYY-MM-DD` form, a real calendar date, and MySQL's supported date range. |

The integer validators use regular expressions before calling `int()`. This
rejects forms such as `+3`, `3.0`, or embedded spaces that the prompt does
not promise to accept. The length guard also prevents attempting to convert
an unnecessarily enormous numeric string.

Price validation uses `Decimal` rather than `float`. Binary floating-point
cannot represent many decimal fractions exactly; `Decimal` is appropriate
for a monetary field. The regular expression caps accepted notation and
fractional digits, while the numeric comparisons enforce the SQL column's
actual range.

Date validation separates text-shape checking from calendar checking. A
string such as `2025-02-31` has the right shape but is not a real date, so
`date.fromisoformat()` rejects it. A future date is not itself invalid:
planning entries are allowed and the current summary excludes dates beyond
its cutoff.

[`read_car_details(is_update=False)`](car_company.py#L387) composes the model,
price, manufacturer, year, color, and electric validators into one tuple.
When called for an update, it changes the prompt wording to say “New”; it
does not use a different validation policy. The model-year upper limit is
recomputed on each call from the current date.

[`get_record_config(table)`](car_company.py#L405) checks that a shared
production/sales operation was given a supported key and returns its
configured ID column, date column, and title. It raises `ValueError` for
unknown table names rather than constructing an SQL identifier from them.
[`read_record_details(table)`](car_company.py#L412) collects the fields
specific to the selected record kind and raises the same kind of error for
unsupported input. These guards protect function boundaries even if a future
caller bypasses the menus.

### Error reporting and resource cleanup

[`show_error_details(error)`](car_company.py#L459) converts exception text
through [`visible_text()`](car_company.py#L91) and wraps it to a terminal
width. The fallback width keeps formatting usable when the terminal cannot
report its dimensions.

[`report_database_error(connection, error, message)`](car_company.py#L466)
prints a context-specific message, then the connector's detail, and attempts
`rollback()`. If rollback itself fails, that second error is also displayed
and re-raised. The re-raise matters: callers can distinguish “the operation
failed but cleanup completed” from “cleanup also failed.” Since the
connection uses autocommit, rollback is an attempt at cleanup; it cannot
undo a statement MySQL has already committed.

[`close_cursor(cursor)`](car_company.py#L478) centralizes cursor closure and
reports connector errors from `cursor.close()`. It is called from `finally`
blocks in query functions, so normal query errors do not skip cleanup.
[`close_connection(connection)`](car_company.py#L193) is the corresponding
connection-level helper. These functions report cleanup failures explicitly
instead of silently treating them as successful.

### Car queries and CRUD

**CRUD** means create, read, update, and delete. The car functions separate
querying, display, and mutation so that the same rows can serve both the user
interface and later input validation.

| Function | What it does and what it returns |
| --- | --- |
| [`fetch_cars(connection)`](car_company.py#L488) | Runs a fixed ordered `SELECT`, fetches all seven columns, closes the cursor, and returns row tuples. It has no display side effect. |
| [`show_cars(connection)`](car_company.py#L501) | Calls `fetch_cars()`, prints a heading and either an empty-state message or a formatted table, then returns the raw rows for later ID selection. |
| [`add_car(connection)`](car_company.py#L531) | Gathers a validated car tuple, parameterizes one `INSERT`, commits, and reports success. A connector error is shown with duplicate-model context. |
| [`update_car(connection)`](car_company.py#L552) | Displays cars, requires a listed ID, gathers complete replacement details, and updates exactly that key. It reports changed, unchanged, or missing status. |
| [`confirm_delete()`](car_company.py#L589) | Loops until the user explicitly enters `y` or `n`, returning a Boolean. It does not perform deletion itself. |
| [`delete_car(connection)`](car_company.py#L600) | Requires an existing displayed car and affirmative confirmation before issuing a parameterized delete. A foreign key can reject deletion while activity rows exist. |

`fetch_cars()` returns a tuple for each row in this order:

```text
(car_id, model, price, manufacturer, model_year, color, is_electric)
```

`show_cars()` unpacks those positions and builds separate display tuples.
For example, the Boolean is rendered as “Yes” or “No”, while the original
database tuple is returned unchanged. Keeping the original rows matters:
callers extract valid IDs from exactly the cars the user was shown.

The add and update paths reuse [`read_car_details()`](car_company.py#L387),
so both operations apply the same limits and field ordering. SQL values are
passed separately from the query text. The model's unique constraint remains
necessary even with input validation: a second client could create the same
model after this program checked the list.

For an update, MySQL can report zero changed rows either because the ID does
not exist or because the submitted values equal the current values.
[`report_update_result()`](car_company.py#L902) runs a separate existence
query to distinguish those cases. A deletion is different: its affected-row
count directly indicates whether a row was removed. Neither result should be
assumed from the input list alone, since another client may change the
database between display and mutation.

### Production and sales operations

The program shares the same four operation functions for both record types.
The table, key, date, and extra fields are selected using trusted settings,
while the record-specific prompts and labels remain distinct.

| Function | Behavior |
| --- | --- |
| [`show_records(connection, table)`](car_company.py#L626) | Checks the record type, joins records to cars for readable model names, displays the result, and returns raw rows for selecting a record ID. |
| [`add_record(connection, table)`](car_company.py#L688) | Requires at least one car, validates the selected car/date/quantity/extra details, and inserts one record with bound values. |
| [`update_record(connection, table)`](car_company.py#L724) | Requires an existing record and car, then updates its car link, date, quantity, and all record-specific fields in one statement. |
| [`delete_record(connection, table)`](car_company.py#L776) | Requires a listed record and explicit confirmation, then deletes only the selected production or sales row. |

[`show_records()`](car_company.py#L626) returns rows in this general order:

```text
(record_id, car_id, model, event_date, quantity, extra_values...)
```

The SQL joins the selected record table to `cars`, so the user sees the
model name without duplicating that name in production or sales storage.
Boolean extras are converted for display only. The return value remains the
raw query result because update and delete actions need its record IDs.

[`add_record()`](car_company.py#L688) first shows cars and stops if none
exist. This is a user-friendly guard; the foreign key is still the database
guarantee that a referenced car exists. Pressing Enter at the add-date prompt
chooses today's date. The function assembles a column sequence, the same
number of placeholders, and a matching values tuple. Keeping these three
orders aligned is essential: each placeholder receives the value at the same
position.

[`update_record()`](car_company.py#L724) does not modify the primary key. It
selects a record by its configured key, validates a replacement car, then
reads and updates all mutable fields together. This gives one coherent
statement instead of several partial updates. It uses
[`report_update_result()`](car_company.py#L902) to handle unchanged values.

[`delete_record()`](car_company.py#L776) is intentionally narrow. It removes
only the chosen record, not its car and not records in the other table. The
confirmation loop is separate from SQL execution, which makes the destructive
step easy to review and test.

### Summary and menu functions

[`get_totals(connection, table, as_of=None)`](car_company.py#L801) is a
query helper. It checks the table through `get_record_config()`, defaults
the date cutoff to today's local date, then returns a dictionary mapping
each car ID to the sum of qualifying quantities. The database can return no
row for a car with no activity; `show_summary()` supplies zero for that
missing dictionary entry.

[`show_summary(connection)`](car_company.py#L817) fetches cars once, captures
one cutoff date, obtains production and sales totals separately, then
calculates `produced - sold` for every car. A car with no entries remains
visible. Negative results are preserved because the application reports
recorded arithmetic; it does not enforce an inventory policy.

[`manage_cars(connection)`](car_company.py#L849) maps choices to car
functions with a dictionary. [`manage_records(connection, table)`](car_company.py#L875)
uses a conditional chain because each action needs the `table` argument.
Both loops clear the terminal where appropriate, redraw a heading, read a
choice, show a validation message for unsupported choices, and pause after
the action. The `0` choice returns from the section manager to its caller.

[`report_update_result(...)`](car_company.py#L902) centralizes the
changed/unchanged/missing distinction. Its arguments include the messages
because cars and operational records should report different nouns while
using identical result logic. It reads `cursor.rowcount`; when that is zero,
it runs a parameterized `SELECT 1` for the target key and calls `fetchone()`.
This function relies on trusted table and column names supplied by the
calling operation.

[`main()`](car_company.py#L924) coordinates setup, the main menu, operation
dispatch, outer error handling, and shutdown. It owns the long-lived
connection and passes it into submenus. A startup failure prevents entry to
the menu; a recoverable connector error during menu use is shown and returns
control to the user. If rollback fails, the loop exits because the connection
cannot be assumed usable. Keyboard interruption and end-of-file input are
treated as requests to leave, and `finally` performs connection cleanup.

The [main guard](car_company.py#L999) is the boundary between importing and
running. It lets unit tests import the functions without connecting to
MySQL, while `python car_company.py` starts the interactive application.

## Data Contracts and Query Shapes

Small applications are easier to maintain when each layer agrees on the
shape and type of data it receives. This section records those agreements so
that changes to the schema, validators, and display code stay coordinated.

### Field-to-Python-to-MySQL mapping

| Field | Terminal input becomes | MySQL column | Constraints checked by the app |
| --- | --- | --- | --- |
| Car model | `str` | `VARCHAR(50)` | 1–50 printable characters; unique constraint enforced by MySQL. |
| Price | `Decimal` | `DECIMAL(10,2)` | Greater than zero, at most 99,999,999.99, at most two fractional digits. |
| Manufacturer | `str` | `VARCHAR(50)` | 1–50 printable characters after trimming. |
| Model year | `int` | `SMALLINT UNSIGNED` | 1886 through current year + 2. |
| Color | `str` | `VARCHAR(30)` | 1–30 printable characters after trimming. |
| Electric flag | `bool` | `BOOLEAN` | Explicit yes/no answer. |
| Car or record ID | `int` | `INT` primary/foreign key | Must match a displayed ID before an operation continues. |
| Production or sale date | ISO `str` | `DATE` | Real calendar date in MySQL's date range; future dates are allowed. |
| Quantity | `int` | `INT` | 1 through 2,147,483,647. |
| Production shift | `str` | `VARCHAR(20)` | 1–20 printable characters after trimming. |
| Quality checked | `bool` | `BOOLEAN` | Explicit yes/no answer. |
| Sales channel | `str` | `VARCHAR(30)` | 1–30 printable characters after trimming. |
| Payment method | `str` | `VARCHAR(20)` | 1–20 printable characters after trimming. |
| Warranty months | `int` | `SMALLINT UNSIGNED` | 0 through 65,535. |

The application-level checks improve feedback, but the schema also applies
constraints such as `NOT NULL`, uniqueness, and foreign keys. These layers
serve different purposes: the validator explains what to correct, while the
database protects stored data from other clients and race conditions.

### Row shapes and column order

Queries return tuples. A tuple position has meaning only together with the
`SELECT` column list, so changing a query's selected columns requires
reviewing every consumer that unpacks or indexes the row.

| Query/helper | Row or value shape | Main consumer |
| --- | --- | --- |
| [`fetch_cars()`](car_company.py#L488) | `(car_id, model, price, manufacturer, model_year, color, is_electric)` | [`show_cars()`](car_company.py#L501), [`show_summary()`](car_company.py#L817), and ID-selection workflows. |
| [`show_records()`](car_company.py#L626) | `(record_id, car_id, model, date, quantity, extras...)` | Record update/delete workflows and display formatting. |
| [`get_totals()`](car_company.py#L801) | `{car_id: quantity_sum}` | [`show_summary()`](car_company.py#L817). |
| [`read_car_details()`](car_company.py#L387) | `(model, price, manufacturer, model_year, color, is_electric)` | Car insert and update. |
| [`read_record_details()`](car_company.py#L412) | Production: `(shift, quality_checked)`; sales: `(sales_channel, payment_method, warranty_months)` | Record insert and update. |

The same value order appears in several places: schema definition, query
selection, tuple unpacking, `INSERT` column list, placeholder order, and
display headers. When adding a field, update each related contract deliberately
instead of assuming that adding a database column automatically updates the
Python tuples.

### SQL parameter rules

For user values, the connector executes a statement and a separate parameter
sequence:

```python
cursor.execute(
    "UPDATE cars SET model = %s WHERE car_id = %s",
    (model, car_id),
)
```

The placeholders correspond to values in order. The connector handles the
appropriate quoting and type conversion. Do not wrap placeholders in quotes,
and do not use Python's `%`, `.format()`, or f-string interpolation to put
user data into the SQL command.

Identifiers are different: placeholders cannot represent a table or column
name. Shared production/sales functions interpolate identifiers from
[`RECORDS`](car_company.py#L40) and [`RECORD_COLUMNS`](car_company.py#L48),
which are fixed by the program. If a new supported table is added, validate
its key through [`get_record_config()`](car_company.py#L405) and keep the
identifier map internal; never pass raw user text as an identifier.

The query helper [`report_update_result()`](car_company.py#L902) also builds
a table/key existence query. Its callers pass the fixed identifiers used by
the app. Values such as `item_id` remain a `%s` parameter.

### Relationship and deletion rules

`cars.car_id` is the parent key. `production.car_id` and `sales.car_id` are
foreign keys pointing to it. This relationship means:

- A production or sales row cannot refer to a non-existent car.
- A car with child rows cannot be deleted while the foreign-key constraint
  remains active.
- Deleting one production row does not delete the car or its sales.
- Removing a car intentionally requires removing its production and sales
  rows first, or choosing a different data-retention policy.

The program does not define cascading deletion. This conservative behavior
reduces the chance that one menu action removes more records than the user
expected.

## End-to-End Operations

These are optional worked examples, not additional program stages. The
[Detailed Script Walkthrough](#detailed-script-walkthrough) explains each
component; these traces show how the components fit together for a complete
user action.

### Starting the application

1. Python evaluates imports and configuration. No menu or database request
   occurs just because the module has been imported.
2. The main guard calls [`main()`](car_company.py#L924) only when the file is
   run as the script.
3. `main()` calls [`connect_to_database()`](car_company.py#L203). The user
   enters connection settings; the password uses `getpass`.
4. The connector creates the database if needed, then opens a connection
   scoped to that database.
5. `main()` calls [`create_tables()`](car_company.py#L247). New installations
   receive all tables; older installations receive configured missing
   columns.
6. Once setup succeeds, the menu loop begins. A setup error is shown before
   normal menu operations are available.

If startup fails, investigate in this order: is MySQL running and reachable;
is the host/user/password correct; can the account create the database and
tables; is the connector package installed; and does the existing schema have
an incompatible old column or constraint? The displayed connector detail
helps separate a network refusal from a permission problem.

### Adding a car

1. The main menu passes the shared connection into
   [`manage_cars()`](car_company.py#L849).
2. Choosing “Add a car” invokes [`add_car()`](car_company.py#L531).
3. [`read_car_details()`](car_company.py#L387) calls the model, price, text,
   integer-range, and yes/no validators in a fixed order.
4. The returned values are unpacked into local names. Their order matches
   the `INSERT` column list.
5. `add_car()` opens a cursor and calls `execute(sql, values)`. Every input
   value is bound separately; the generated `car_id` is omitted.
6. Autocommit persists the successful statement. The explicit `commit()` is
   still called, then a short confirmation is printed.
7. The cursor closes in `finally`, and the submenu pauses before redrawing.

If the model already exists, the unique index rejects the insert. The
application reports an add failure rather than retrying the model field,
because only MySQL can definitively detect a duplicate that another client
may insert concurrently.

### Adding a production or sales record

These are nearly the same flow, with the selected table controlling the
event date and extra fields:

| Step | Production | Sales |
| --- | --- | --- |
| Menu route | `manage_records(connection, "production")` | `manage_records(connection, "sales")` |
| Date label | Production date | Sale date |
| Record details | Shift and quality-check answer | Channel, payment method, warranty months |
| Key/date columns | `production_id`, `production_date` | `sale_id`, `sale_date` |

Both use [`add_record()`](car_company.py#L688). It first calls
[`show_cars()`](car_company.py#L501). An empty car list ends the operation
with a helpful message. Otherwise, the ID validator restricts the choice to
the displayed list; the database foreign key remains the final check.

The record date can default to today on an add, but a future date is valid for
planning. The summary later filters by date. After reading a positive
quantity and type-specific details, the operation constructs a complete
insert with one placeholder per supplied value. The selected table and field
names come from fixed configuration; every data value is passed separately.

### Updating an existing row

The update path first presents available rows. It avoids asking for an ID
when no target exists. A selected ID must belong to that list, and a record
update additionally requires a car to reassign the record to. Each editable
value is then collected before SQL is executed.

This “collect first, write once” approach has two benefits. A rejected
terminal value does not leave a partially updated row, and all fields in the
statement refer to the same selected record. The SQL `WHERE` uses the
primary-key value. On success, the helper distinguishes:

| Connector result | Existence check | Meaning to the user |
| --- | --- | --- |
| One or more affected rows | Not needed | The record changed. |
| Zero affected rows | Matching key exists | The submitted values were already stored. |
| Zero affected rows | No matching key | The record no longer exists, perhaps due to another client. |

The last case is why the displayed list is not treated as a permanent lock:
another client can change or delete a row after the list was fetched.

### Deleting a row

Deletion separates **selection**, **confirmation**, and **execution**:

1. Fetch and display the current candidates.
2. Validate that the requested ID appears in that result.
3. Ask for explicit `y` or `n`; anything else repeats the question.
4. Return without SQL if the answer is no.
5. Execute a parameterized `DELETE` by primary key and inspect `rowcount`.

For a car, the database may reject step 5 while related production or sales
rows exist. The error message explains the required action; the application
does not silently cascade the deletion. For a production or sales row, only
the selected record is removed.

### Producing the summary

[`show_summary()`](car_company.py#L817) fetches all cars first so that cars
with no production or sales still appear. It captures the current local date
once and passes it to both [`get_totals()`](car_company.py#L801) calls.
Each query sums quantities grouped by `car_id` for rows whose event date is
on or before the cutoff.

For each car, missing dictionary keys become zero. The report then subtracts
sales from production. Future records do not affect today's report, but they
remain in the database and will count once their date falls within the
cutoff. The report is descriptive, not a stock-control system: it does not
prevent a user recording sales greater than production.

Separate production and sales aggregate queries are intentional. A single
join of two one-to-many tables could multiply production rows by sales rows.
For example, two production entries joined to three sales entries can create
six combined rows; summing those joined values would overcount both totals.
Aggregating each side independently and then matching by car ID avoids that
fan-out error.

## Reliability, Errors, and Edge Cases

### Error layers

Errors are handled close to where the program can explain or recover from
them:

| Layer | Example | Expected response |
| --- | --- | --- |
| Input validator | Invalid date or out-of-range quantity | Explain the accepted format/range and ask again. |
| Shared function boundary | Unsupported table string | Raise `ValueError`; do not build a query from the unknown identifier. |
| CRUD operation | Duplicate model or invalid foreign key | Print a contextual message and database details; attempt rollback; close the cursor. |
| Menu-level safety net | Connector error from a read or a propagated operation | Show details, attempt rollback, then pause or exit if the connection is unusable. |
| Startup | Connection or schema initialization failure | Explain that startup failed, close an opened connection if possible, and do not enter the menu. |
| Cleanup | Cursor or connection close failure | Report the cleanup error rather than hiding it. |

An exception message is not a substitute for context. “Could not add car”
identifies the action; the connector detail helps diagnose the database cause.
Conversely, do not catch every exception and continue as if the operation
succeeded. The code catches expected input/connector/interruption failures
at defined boundaries.

### Autocommit and transaction expectations

[`connect_to_database()`](car_company.py#L203) enables autocommit. Therefore,
each successful data-changing statement is immediately committed by MySQL.
The operation functions still call `commit()` as an explicit success marker,
but a later `rollback()` cannot undo an already committed statement.

Current CRUD operations execute one data-changing statement each, so they do
not require a multi-statement transaction to make one row change atomic. Do
not document a rollback as restoring a row if an error occurred after its
statement committed. If a future feature needs several related writes to
succeed or fail as one unit, it must deliberately revise the transaction
settings and test the behavior with a real MySQL server; merely adding more
`commit()` calls will not create that atomic group.

Schema setup has a separate limitation: MySQL DDL may auto-commit. An
`ALTER TABLE` that completed before a later schema error may remain applied.
The migration is designed to be rerunnable by inspecting existing columns,
not by promising a full rollback of all schema changes.

### Time and date boundaries

Dates in this application represent calendar days, not instants in a time
zone. `date.today()` uses the machine's local date. The summary captures it
once per report; it does not call `today()` separately for production and
sales.

The accepted SQL date range starts at `1000-01-01`; the upper supported
Python/MySQL date is `9999-12-31`. The app accepts future dates for planned
activity but excludes them from totals until the chosen cutoff reaches them.
This policy means a future sale can be stored without appearing in today's
sales total.

Model-year bounds are independent of activity dates. The oldest permitted
year is the configured constant 1886; the upper bound follows the current
year plus the configured future allowance. Warranty months use an unsigned
small integer range that includes zero, while quantity must be positive.

### Terminal and Unicode behavior

Terminal output may be redirected, narrow, or contain Unicode text:

- Clearing is gated by terminal checks, so logs are not erased.
- Terminal-size lookup has fallback dimensions, so non-interactive sessions
  still have a usable layout.
- Tables shrink wide columns and clip values rather than wrapping rows.
- Wide East Asian code points count as two cells; combining marks count as
  zero additional cells.
- Stored control characters are escaped before printing.

These measures improve readability and reduce surprising output; they do
not make every terminal emulator behave identically. In particular, emoji
and multi-code-point grapheme clusters may occupy a different number of
cells than the simple width estimator predicts.

### Concurrency and time-of-check/time-of-use cases

The program displays a list before a user selects an ID. Another database
client can alter the database between the display and the later query. The
application therefore uses the list as a usability filter, not as a lock:

- A delete may affect zero rows if another client deleted the item first.
- An update may report “No record found” if its key disappeared.
- A duplicate model may be created by another client after the current list
  was displayed; the unique constraint still catches the conflict.
- A referenced car might be deleted elsewhere after it was listed; the
  foreign key still validates the attempted insert or reassignment.

The database constraints are the final authority for invariants that must
hold across multiple clients. The UI cannot guarantee them merely by
checking the current display.

## How to Extend the Program

Schema and program changes should be treated as a coordinated set of
contracts. A feature is not complete just because a column appears in
`CREATE TABLE`; its input, migration, SQL, output, tests, and documentation
may also need updates.

### Adding a field to an existing entity

Use this sequence for a new car, production, or sales field:

1. **Choose the SQL type and bounds.** Consider whether the field is text,
   integer, decimal, Boolean, or date, and define `NULL`, uniqueness, and
   defaults deliberately.
2. **Update the new-table definition** in [`create_tables()`](car_company.py#L247).
3. **Update the migration map** (`CAR_COLUMNS` or the appropriate entry in
   `RECORD_COLUMNS`) so existing installations gain the field with a safe
   default.
4. **Add or reuse a validator** near the other [`read_*()` functions](car_company.py#L306).
5. **Add it to the collector tuple** in [`read_car_details()`](car_company.py#L387)
   or [`read_record_details()`](car_company.py#L412).
6. **Update SQL and parameter order** in add/update operations. Keep column
   names, placeholders, and values aligned.
7. **Update selected columns and tuple consumers** in [`fetch_cars()`](car_company.py#L488)
   or [`show_records()`](car_company.py#L626).
8. **Update visible table headers and output formatting** in
   [`show_cars()`](car_company.py#L501) or [`show_records()`](car_company.py#L626).
9. **Add tests** for accepted/rejected boundaries, SQL parameters, display,
   and migration from the old layout.
10. **Update the schema table and guide references** so the documentation
    agrees with the implemented behavior.

For a `NOT NULL` field added to a populated table, specify a migration
default compatible with the intended SQL type. Do not use a default that
misrepresents important historical information without making that choice
clear in the UI or documentation.

### Adding a new record type

A third record type is broader than adding a single field. The existing
shared workflows assume each record has an integer primary key, a related
`car_id`, a date, a quantity, and configured extra fields. A new type should
first be checked against those assumptions.

If it fits the shared model, coordinate these locations:

- Add trusted key/date/title metadata to [`RECORDS`](car_company.py#L40).
- Add a user-facing date label to [`RECORD_DATE_LABELS`](car_company.py#L44).
- Define its extra field DDL in [`RECORD_COLUMNS`](car_company.py#L48).
- Create its table and include it in the migration loop in
  [`create_tables()`](car_company.py#L247).
- Add record-specific prompts to [`read_record_details()`](car_company.py#L412).
- Route a menu choice in [`main()`](car_company.py#L924).
- Extend any display labels in [`show_records()`](car_company.py#L626).
- Add schema, prompt, operation, summary, and failure-path tests.

Do not add raw user-selected table names. The record type should be chosen by
the program's menu and checked against the fixed configuration before it is
used to construct SQL.

### Changing the terminal layout

Prefer to change [`print_heading()`](car_company.py#L73),
[`read_input()`](car_company.py#L83), or [`print_table()`](car_company.py#L126)
rather than adding one-off spacing logic throughout CRUD functions. Before
adjusting a table:

1. Check both the normal terminal width and a narrow width.
2. Check long model/manufacturer text and ensure it is clipped predictably.
3. Check left alignment for labels and right alignment for numeric values.
4. Check a redirected or captured output stream where screen clearing should
   not occur.
5. Check control characters and wide Unicode characters if user/database text
   is displayed.

Keep database values unchanged when formatting them. Escaping and truncation
should affect only the temporary display string.

### Maintaining source references

This guide uses links such as `[add_car()](car_company.py#L531)` to identify
definitions. When code is inserted above those functions, line fragments can
become stale. After a substantial code edit:

- Search the source for every linked function name and confirm each still
  points close to its definition.
- Update the compact [Source-code map](#source-code-map) and the function
  catalog if a responsibility moves.
- Check that Markdown links to project files still resolve.
- Prefer a function-name link over a broad file link when describing one
  implementation detail.

The linked function name is the semantic reference; the line anchor is a
convenience for navigation. If a hosting platform changes its anchor
behavior, the source file still remains the authoritative implementation.

### A focused verification checklist

Before calling a code change complete, run the smallest checks that cover it:

| Change type | Minimum useful checks |
| --- | --- |
| Input validation | Unit tests for valid, invalid, minimum, maximum, and malformed values. |
| SQL operation | Tests for SQL shape, parameter tuple order, result count, error handling, and cursor closure. |
| Schema or migration | Tests for a fresh schema and an older schema missing each new field; confirm no rows are dropped. |
| Summary calculation | Tests with no activity, only production, only sales, multiple rows, future dates, and a shared cutoff. |
| Terminal formatting | Tests for empty rows, narrow width, long text, alignment, control characters, and Unicode width cases. |
| Menu or shutdown | Tests for valid/invalid choices, back/exit behavior, keyboard interruption, end-of-file, and connection cleanup. |
| Documentation | Check local links and source anchors; run `git diff --check`. |

The fake database tests can prove query construction and application logic,
but not MySQL permissions or server-specific DDL behavior. For a release
that changes schema or connector behavior, also test against a disposable
MySQL database, including one created from the previous schema.

## Further Reading

- [Python documentation](https://docs.python.org/3/)
- [Python standard library](https://docs.python.org/3/library/)
- [MySQL Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)
- [MySQL Connector/Python Developer Guide](https://dev.mysql.com/doc/connector-python/en/)
- [Project README](README.md)
- [School project report](project_report.md)
