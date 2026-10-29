# Car Company Database

**Documentation:** [README overview](README.md) | [Programming guide](PROGRAMMING_GUIDE.md) | [CBSE project report](project_report.md)

## Project Overview

This menu-driven project uses Python and MySQL to manage basic car company
records. It stores car models and prices, records production and sales by date,
allows saved rows to be updated or deleted, and displays totals for each model.

At startup, the program asks for the MySQL connection details. The user enters
car models, prices, dates, and quantities through the menus; no project data
needs to be entered by editing the Python file. The program creates the chosen
database and any missing tables. Existing records are kept.

## Objectives

- Store company data in related MySQL tables.
- Use a primary key to identify each row.
- Use foreign keys to connect production and sales records to a car.
- Perform the basic database operations: insert, display, update, and delete.
- Use SQL queries to display joined information and calculate totals.
- Provide a simple menu so the program can be used without editing its code.

## Database Design

The database contains three tables:

| Table | Purpose |
| --- | --- |
| `cars` | One row for each car model and its price. |
| `production` | One row for each production entry. |
| `sales` | One row for each sales entry. |

### Table fields

| Table | Field | Meaning |
| --- | --- | --- |
| `cars` | `car_id` | Unique number for a car; primary key and automatically generated. |
| `cars` | `model` | Car model name; required and unique. |
| `cars` | `price` | Price in rupees, stored with two decimal places. |
| `production` | `production_id` | Unique number for a production entry; primary key. |
| `production` | `car_id` | The car produced; foreign key referring to `cars.car_id`. |
| `production` | `production_date` | Date the production entry was recorded. |
| `production` | `quantity` | Number of cars produced in this entry. |
| `sales` | `sale_id` | Unique number for a sales entry; primary key. |
| `sales` | `car_id` | The car sold; foreign key referring to `cars.car_id`. |
| `sales` | `sale_date` | Date the sales entry was recorded. |
| `sales` | `quantity` | Number of cars sold in this entry. |

### Relationship

One car can have many production entries and many sales entries. Each
production or sales entry belongs to one car:

```text
cars (one) ------ (many) production
cars (one) ------ (many) sales
```

The foreign keys prevent a production or sales entry from referring to a car
that is not in the `cars` table. MySQL also prevents deleting a car while
production or sales entries still refer to it. Delete those entries first if
the car is no longer needed.

## SQL Concepts Used

- `CREATE DATABASE` and `CREATE TABLE` create the database structure.
- `PRIMARY KEY` uniquely identifies a row.
- `AUTO_INCREMENT` lets MySQL assign new ID values.
- `NOT NULL` requires a value; `UNIQUE` prevents duplicate model names.
- `FOREIGN KEY` maintains the relationship between tables.
- `INSERT` adds a row, `SELECT` displays rows, `UPDATE` changes a row, and
  `DELETE` removes a row.
- `WHERE` selects the row to change or remove. `ORDER BY` sorts displayed rows.
- `JOIN` displays a car model with its production or sales records.
- `SUM` calculates totals, and `GROUP BY` calculates a separate total for each
  car.

Python sends entered values to MySQL using `%s` placeholders. This keeps the
user's data separate from the SQL command. Table and column names used in
queries come only from fixed choices inside the program.

## Requirements

- Python 3.8 or newer; Python 3.9 or newer is recommended.
- MySQL Server 8.0 or a compatible server, running locally or reachable over a
  network.
- A MySQL account with permission to create the project database and tables.
- `mysql-connector-python`, installed from `requirements.txt`.
- A keyboard and terminal. Windows, macOS, and Linux terminals are supported.

The Python `unittest` module and all other application modules are included
with Python, so they do not need entries in `requirements.txt`. See the
[Programming Guide](PROGRAMMING_GUIDE.md#system-requirements) for details.

## Download to Desktop

These commands download the project into a folder named
`car_company_mysqldb` on the Desktop, using the repository's `main` branch.

On Linux or macOS:

```sh
mkdir -p "$HOME/Desktop/car_company_mysqldb"
curl -L https://github.com/xzzilch/car_company_mysqldb/archive/refs/heads/main.tar.gz | tar -xz --strip-components=1 -C "$HOME/Desktop/car_company_mysqldb"
```

On Windows PowerShell:

```powershell
$desktop = [Environment]::GetFolderPath('Desktop')
$archive = Join-Path $desktop 'car_company_mysqldb.zip'
curl.exe -L https://github.com/xzzilch/car_company_mysqldb/archive/refs/heads/main.zip -o $archive
Expand-Archive -Force $archive $desktop
Remove-Item $archive
```

On Windows, the extracted folder is named `car_company_mysqldb-main`.

The commands put downloaded project files on the Desktop. They do not install
Python, the MySQL connector, or MySQL Server, and do not download database
records. Records remain in the MySQL database selected when the program runs.
Install the connector and run the program from the downloaded folder as
described below.

## Project Files

- `car_company.py` contains the menu-driven application.
- `tests/test_car_company.py` contains automated tests that do not need MySQL.
- `requirements.txt` lists the Python package required by the application.
- `PROGRAMMING_GUIDE.md` explains Python, MySQL, the schema, and program functions.
- `project_report.md` is a school-submission report template.
- `.gitignore` excludes local environments, caches, and secret files.

Install the connector from a terminal:

```text
python -m pip install -r requirements.txt
```

See [project_report.md](project_report.md) for a school-submission report
template. Fill in its personal details and replace sample results with your own
actual test results before submitting.

## Running the Project

Run the program from its folder:

```text
python car_company.py
```

When both input and output use an interactive terminal, each menu redraw clears
the previous menu. Lists shown during an add or update stay on screen while you
enter values. After an action, press Enter to read its result and return to the
menu. Screen clearing is skipped in non-interactive use.

At startup, enter the MySQL host and username. Press Enter to accept the
suggested host (`localhost`), username (`root`), or database name
(`car_company`). Enter the MySQL password when prompted; the password is not
shown on screen. If the account has no password, press Enter. The database
name may contain letters, numbers, and underscores and must be no longer than
64 characters.

The account must have permission to create the database the first time the
program runs. If the database already exists, it still needs permission to
create the project tables when they are missing.

## Menu Guide

The main menu opens **Manage cars**, **Manage production records**, or
**Manage sales records**, displays the summary, or exits. Each data section
provides these actions:

- **1, View:** displays the saved rows.
- **2, Add:** asks for the values needed for a new row.
- **3, Update:** asks for a row ID from the displayed list, then asks for all
  replacement values. An update replaces all editable values in that row.
- **4, Delete:** asks for a row ID and requires confirmation.
- **0, Back:** returns to the main menu.

For a production or sales entry, first add the car in **Manage cars**. Use a
car ID shown in the list. Update and delete operations also accept only IDs
shown in the relevant list. Dates must use `YYYY-MM-DD` and fall within
MySQL's `1000-01-01` to `9999-12-31` range. When adding an entry,
press Enter at the date prompt to use today's date; updates require a date.
Prices must be greater than zero and have at most two decimal places.
Quantities and IDs must be positive whole numbers that fit the MySQL `INT`
type. A car model must contain 1 to 50 characters and cannot duplicate another
model.

## Example Run

The examples below show a fresh database and sample inputs. Text in square
brackets is an explanation, not something to type. The password is not echoed
by the terminal. Automatically assigned IDs can differ if the database already
contains records. Repeated menu redraws and "Press Enter to continue" prompts
are omitted where they do not change the example.

### Start and Add a Car

```text
$ python car_company.py

-----------------------
  DATABASE CONNECTION
-----------------------
MySQL host [localhost]: [press Enter]
MySQL username [root]: [press Enter]
MySQL password (press Enter if none): [press Enter; input stays hidden]
Database name [car_company]: [press Enter]

-------------
  MAIN MENU
-------------
1 Cars | 2 Production | 3 Sales
4 Summary | 0 Exit
Choose an option: 1

-------------
  CARS MENU
-------------
1 View | 2 Add | 3 Update | 4 Delete | 0 Back
Choose an option: 2
Car model: City LX
Price (Rs.): 1250000.00
Car added.
```

### Record Production

Continuing the same run, choose `0` to return to the main menu, then choose
`2` to manage production and `2` again to add a record:

```text
Choose an option: 0

-------------
  MAIN MENU
-------------
1 Cars | 2 Production | 3 Sales
4 Summary | 0 Exit
Choose an option: 2

-------------------
  PRODUCTION MENU
-------------------
1 View | 2 Add | 3 Update | 4 Delete | 0 Back
Choose an option: 2

--------
  CARS
--------
ID 1 | City LX | Rs. 1250000.00
Car ID: 1
Date (YYYY-MM-DD) [today]: 2026-10-23
Quantity: 120
Record added.
```

### Record a Sale

Return to the main menu with `0`, choose **Manage sales records**, and add a
record. This example uses the same car:

```text
Choose an option: 0

-------------
  MAIN MENU
-------------
1 Cars | 2 Production | 3 Sales
4 Summary | 0 Exit
Choose an option: 3

--------------
  SALES MENU
--------------
1 View | 2 Add | 3 Update | 4 Delete | 0 Back
Choose an option: 2

--------
  CARS
--------
ID 1 | City LX | Rs. 1250000.00
Car ID: 1
Date (YYYY-MM-DD) [today]: 2026-10-23
Quantity: 35
Record added.
```

### View the Summary

Return to the main menu with `0`, then select the summary. With the sample
production and sales records above, the output is:

```text
Choose an option: 0

-------------
  MAIN MENU
-------------
1 Cars | 2 Production | 3 Sales
4 Summary | 0 Exit
Choose an option: 4

--------------------------------
  PRODUCTION AND SALES SUMMARY
--------------------------------
Car model                      | Produced | Sold | Cars left
City LX                        |      120 |   35 |        85
```

The `Cars left` value is total production minus total sales. A missing total is
shown as zero. Negative values are shown as-is to make sales exceeding
production visible; the program does not enforce stock limits. Long model names
are abbreviated in this summary so the numeric columns stay aligned; the saved
name is unchanged.

## Example Queries

The following are representative queries used by the program. The Python
program uses placeholders when values come from the user.

Display cars in ID order:

```sql
SELECT car_id, model, price
FROM cars
ORDER BY car_id;
```

Display production entries with their car model:

```sql
SELECT production.production_id, cars.model,
       production.production_date, production.quantity
FROM production
JOIN cars ON production.car_id = cars.car_id
ORDER BY production.production_id;
```

Calculate the production total for each car ID:

```sql
SELECT car_id, SUM(quantity)
FROM production
GROUP BY car_id;
```

The summary menu runs this grouped query once for production and once for
sales. It displays zero when a car has no matching entries. Keeping the totals
separate avoids counting entries more than once when both tables contain
multiple rows for the same car. The `Cars left` column is production minus
sales; negative values indicate that recorded sales exceed recorded production.

## Testing Checklist

- Start the program and confirm it creates the database and tables.
- Add a car, then view the Cars list to verify it was saved.
- Add production and sales entries for that car and view each list.
- Update a row and check that the new values are displayed.
- Cancel a delete, then repeat and confirm it; check the list afterward.
- Try an invalid date, zero quantity, a price with more than two decimal
  places, or a non-numeric price. Check that the program asks for valid input.
- Try an ID that is not in the displayed list and a duplicate car model; check
  that the program rejects them without changing saved records.
- Try deleting a car that still has related entries and confirm MySQL protects
  the relationship.
- View the summary and compare its totals with the entries entered.

The automated tests cover input validation, summary output, screen handling,
and startup cleanup. They use Python's built-in `unittest` module and do not
need a running MySQL server. Run them from the project folder:

```text
python -m unittest discover -s tests
```

## Scope and Limitations

This project is intended for learning basic database operations. It does not
include staff accounts, inventory valuation, invoices, graphical screens, or
advanced reporting. Production and sales quantities are recorded as separate
entries; the summary calculates a basic remaining quantity but does not enforce
inventory limits.