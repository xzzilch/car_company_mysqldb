# Programming Guide

This guide explains the ideas and functions used by the Car Company Database program. It is written for a beginner and follows the program's actual design. The program stores records in MySQL; it does not save car data in a local project file.

## Contents

1. [Python](#python)
2. [SQL and MySQL](#sql-and-mysql)
3. [System Requirements](#system-requirements)
4. [Python and MySQL Connector](#python-and-mysql-connector)
5. [Database Tables](#database-tables)
6. [Program Functions](#program-functions)
7. [Imported Modules and Functions](#imported-modules-and-functions)
8. [Useful Built-in Functions and Methods](#useful-built-in-functions-and-methods)
9. [Program Flow](#program-flow)

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
- Provides transactions, so successful changes can be committed and failed work can be rolled back.
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

- **Python:** Python 3.8 or newer is recommended. The installed MySQL Connector/Python release must support the installed Python version.
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
7. `create_tables()` creates missing tables, then calls `commit()`.
8. Operations create cursors, execute SQL, fetch results where needed, and close cursors. Changes are committed on success or rolled back after a connector error.
9. `main()` closes the database connection when the program exits.

The password is read with `getpass`, so normal terminal input does not echo it. The program does not save credentials to a local configuration file. Do not put a real password into source code or commit it to the repository.

### Parameterized values

For inserted, changed, and deleted values, the program uses `%s` placeholders and passes the values separately:

```python
cursor.execute(
    "INSERT INTO cars (model, price) VALUES (%s, %s)",
    (model, price),
)
```

This is safer and more reliable than building a SQL command by joining user text into it. SQL table and column names cannot be supplied as ordinary value placeholders; the program uses fixed table/column names from its `RECORDS` dictionary for those queries.

## Database Tables

The program creates three tables. The `cars` table is the parent. Each production or sales row belongs to one car through `car_id`.

```text
cars (one) ------ (many) production
cars (one) ------ (many) sales
```

The following is the standard tabular layout returned by MySQL's `DESCRIBE` command for the definitions in `create_tables()`. `Default` cells with no displayed value are blank. MySQL versions can format output differently, so run the commands below to see the exact output from your own server.

### `cars`

Command: `DESCRIBE cars;`

```text
+--------+---------------+------+-----+---------+----------------+
| Field  | Type          | Null | Key | Default | Extra          |
+--------+---------------+------+-----+---------+----------------+
| car_id | int           | NO   | PRI | NULL    | auto_increment |
| model  | varchar(50)   | NO   | UNI | NULL    |                |
| price  | decimal(10,2) | NO   |     | NULL    |                |
+--------+---------------+------+-----+---------+----------------+
```

- `car_id` is the primary key and is generated by MySQL.
- `model` is required and unique, so two cars cannot have the same model name.
- `price` is required and stores up to eight digits before and two digits after the decimal point.

### `production`

Command: `DESCRIBE production;`

```text
+-----------------+------+------+-----+---------+----------------+
| Field           | Type | Null | Key | Default | Extra          |
+-----------------+------+------+-----+---------+----------------+
| production_id   | int  | NO   | PRI | NULL    | auto_increment |
| car_id          | int  | NO   | MUL | NULL    |                |
| production_date | date | NO   |     | NULL    |                |
| quantity        | int  | NO   |     | NULL    |                |
+-----------------+------+------+-----+---------+----------------+
```

- `production_id` is the generated primary key for a production entry.
- `car_id` is a foreign key to `cars.car_id`. MySQL commonly displays its index as `MUL` because multiple production rows can refer to the same car.
- `production_date` stores the date of the entry.
- `quantity` stores the number made in this entry.

### `sales`

Command: `DESCRIBE sales;`

```text
+-----------+------+------+-----+---------+----------------+
| Field     | Type | Null | Key | Default | Extra          |
+-----------+------+------+-----+---------+----------------+
| sale_id   | int  | NO   | PRI | NULL    | auto_increment |
| car_id    | int  | NO   | MUL | NULL    |                |
| sale_date | date | NO   |     | NULL    |                |
| quantity  | int  | NO   |     | NULL    |                |
+-----------+------+------+-----+---------+----------------+
```

- `sale_id` is the generated primary key for a sales entry.
- `car_id` is a foreign key to `cars.car_id`.
- `sale_date` stores the date of the entry.
- `quantity` stores the number sold in this entry.

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

### Terminal and connection

- **`clear_screen()`** checks that standard input and output are terminals. It then uses `os.system()` to call `cls` on Windows or `clear` on other systems. Redirected output is not cleared.
- **`print_heading(title)`** prints a heading with a divider sized to the title.
- **`pause_for_menu()`** waits for Enter so the user can read an operation's result before the next menu.
- **`connect_to_database()`** reads connection details, checks the database name, creates the database if needed, and returns a connection to it.
- **`create_tables(connection)`** creates the three tables if they do not already exist and commits the schema changes.

### Input checking and errors

- **`read_positive_integer(message)`** repeats the prompt until it receives an integer from 1 through the MySQL signed `INT` maximum used by this program.
- **`read_price(message)`** repeats until the input is a finite positive decimal that fits `DECIMAL(10, 2)` and has no more than two decimal places.
- **`read_model(message)`** accepts a non-empty model name of at most 50 characters.
- **`read_existing_id(message, valid_ids)`** accepts only an ID from the IDs in the list already displayed.
- **`read_date(message, default_today=False)`** validates a real MySQL `DATE` value in `YYYY-MM-DD` form. When `default_today=True`, empty input means today's date.
- **`show_error_details(error)`** prints a connector error wrapped to fit the detected terminal width, using 80 columns as a fallback.
- **`confirm_delete()`** accepts only `y` or `n` and returns `True` only for `y`.

### Car operations

- **`fetch_cars(connection)`** selects all car IDs, models, and prices in ID order and returns the rows.
- **`show_cars(connection)`** prints the car list and returns the same rows for later ID validation.
- **`add_car(connection)`** reads a model and price, inserts a car, commits on success, and rolls back and reports a connector error on failure.
- **`update_car(connection)`** displays cars, validates the selected ID, reads replacement model and price, and updates only that row.
- **`delete_car(connection)`** displays cars, validates the chosen ID, asks for confirmation, and deletes that car. A foreign-key error protects cars that still have production or sales rows.

### Production and sales operations

- **`show_records(connection, table)`** reads rows from the fixed `production` or `sales` table, joins each row to its car model, prints the results, and returns them for ID selection.
- **`add_record(connection, table)`** lists cars, validates the selected car, reads a date and quantity, and inserts one production or sales entry.
- **`update_record(connection, table)`** lists entries, validates the record and car IDs, reads replacement values, and updates the selected entry.
- **`delete_record(connection, table)`** lists entries, validates the chosen ID, confirms the action, and deletes the selected entry.
- **`get_totals(connection, table)`** runs `SUM(quantity)` grouped by car and returns a dictionary mapping each car ID to its total.

The `table` argument is expected to be one of the fixed keys in `RECORDS`; it is not free-form user input.

### Summary and application flow

- **`show_summary(connection)`** loads cars and the two totals, treats a missing total as zero, calculates `produced - sold`, and prints the `Cars left` column. Long model names are abbreviated for alignment; negative balances remain visible.
- **`manage_cars(connection)`** displays the car menu, dispatches the selected action, pauses after an action, and returns on option 0.
- **`manage_records(connection, table)`** displays the production or sales menu and routes the selected action to the appropriate function.
- **`main()`** connects to MySQL, creates missing tables, runs the main menu, handles database and keyboard errors, and closes the connection.

## Imported Modules and Functions

This section explains every imported module and imported API used by `car_company.py`.

| Import | Use in this program |
| --- | --- |
| `datetime.date` | Creates and validates calendar dates; `today()`, `fromisoformat()`, and `isoformat()` are used. |
| `decimal.Decimal` | Parses and compares prices without binary floating-point rounding. |
| `decimal.InvalidOperation` | Exception caught when price text is not a valid decimal. |
| `getpass.getpass` | Reads the MySQL password without echoing the typed characters. |
| `os.name` | Identifies the operating system (`nt` for Windows). |
| `os.system(command)` | Runs the terminal clear command (`cls` or `clear`). |
| `re.fullmatch(pattern, text)` | Checks that the complete database name contains only allowed letters, digits, or underscores. |
| `shutil.get_terminal_size(fallback)` | Gets terminal width for formatting database error messages; uses the fallback if size detection fails. |
| `sys.stdin` and `sys.stdout` | Refer to standard input and output; their `isatty()` methods identify interactive terminals. |
| `textwrap.fill(text, width)` | Wraps long error text to a selected width. |
| `mysql.connector.connect(**settings)` | Opens a MySQL connection using the supplied host, user, password, and optional database. |
| `mysql.connector.Error` | Base exception used to catch connector and database errors. |

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

MySQL Connector/Python also supplies the following objects and methods used in the code: `connection.cursor()` creates a cursor; `cursor.execute()` sends SQL to the server; `cursor.fetchall()` returns query rows; `cursor.rowcount` reports affected rows for updates and deletes; `connection.commit()` saves a transaction; `connection.rollback()` cancels the current transaction; `cursor.close()` and `connection.close()` release resources; and `connection.is_connected()` checks whether the connection is still open.

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

The test fixtures' `execute()`, `fetchall()`, and `close()` methods imitate the small part of a MySQL cursor used by summary tests. They do not connect to a real database.

## Program Flow

1. `main()` opens a MySQL connection and creates any missing tables.
2. The main menu routes to car management, production management, sales management, the summary, or exit.
3. Input helper functions validate values before database operations.
4. SQL statements run through connector cursors; values use `%s` placeholders.
5. Successful data changes are committed. Connector errors trigger rollback and a readable error message.
6. The summary adds production totals and sales totals separately, then computes `Cars left = Produced - Sold` for each car.
7. On exit, `main()` closes the database connection.

## Further Reading

- [Python documentation](https://docs.python.org/3/)
- [Python standard library](https://docs.python.org/3/library/)
- [MySQL Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)
- [MySQL Connector/Python Developer Guide](https://dev.mysql.com/doc/connector-python/en/)
- [Project README](README.md)
