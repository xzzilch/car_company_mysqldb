# Car Company Database Project Report

> Complete the bracketed personal details before submitting. Ask your teacher
> whether your school requires a specific certificate or acknowledgement
> format. Do not sign or certify this report on behalf of another person.

## Cover Page

**Project title:** Car Company Database Management System  
**Subject:** Computer Science (083)  
**Academic session:** [Session]  
**Student name:** [Student name]  
**Class and section:** XII [Section]  
**Roll number:** [Roll number]  
**School:** [School name]  
**Teacher:** [Teacher name]

## Certificate

This is to certify that **[Student name]**, of Class XII **[Section]**, Roll
Number **[Roll number]**, has completed the Computer Science project titled
**Car Company Database Management System** for the academic session
**[Session]**, under my guidance.

**Teacher's signature:** ____________________  
**External examiner's signature:** ____________________  
**Date:** ____________________  
**School seal:** ____________________

> This is a template. The teacher and school should review and complete the
> certificate according to their requirements.

## Acknowledgement

I would like to thank **[Teacher name]** for guidance during this project. I
also thank **[School name]**, my classmates, and my family for their support.
This project helped me practise Python programming and basic relational
database concepts using MySQL.

## Index

| Section | Page |
| --- | --- |
| Project Overview | [Page] |
| Objectives | [Page] |
| Requirements | [Page] |
| Database Design | [Page] |
| Program Logic | [Page] |
| SQL Concepts Demonstrated | [Page] |
| Sample Run and Testing | [Page] |
| Limitations and Future Scope | [Page] |
| Bibliography | [Page] |

Update page numbers after arranging or printing the final report.

## Project Overview

The [Car Company Database Management System](car_company.py) is a menu-driven Python program
connected to a MySQL database. It stores car models and prices and records
production and sales quantities by date. The program can display, add, update,
and delete records, and show production, sales, and cars left for each model.

The program creates the selected database and any missing tables when it
starts. The user supplies connection details and enters project data through
the menus instead of changing variables in the source code.

See the [README](README.md) for setup and sample runs, and the
[programming guide](PROGRAMMING_GUIDE.md) for detailed explanations of the
source code and its functions.

## Objectives

- Store data in related MySQL tables.
- Use primary keys and foreign keys to identify and relate rows.
- Perform insert, display, update, and delete operations.
- Use a join to display record details with a car model.
- Use `SUM` and `GROUP BY` to calculate totals for each car.
- Calculate cars left by subtracting total sales from total production.
- Validate user input and handle common database errors.

## Requirements

### Hardware

- Computer capable of running Python and MySQL Server.
- Keyboard and display for the command-line interface.

### Software

- Python 3.8 or newer. The selected `mysql-connector-python` release must
    support the installed Python version.
- MySQL Server.
- Python package `mysql-connector-python`.

Install the Python package with:

```text
python -m pip install -r requirements.txt
```

Run the program with:

```text
python car_company.py
```

The MySQL account must be permitted to create the database and tables. The
default connection prompts suggest host `localhost`, username `root`, and
database `car_company`; a password is entered privately.

The README provides curl commands to download the project into a folder on the
Desktop. Downloading does not install Python, the connector, or MySQL Server.
Car records remain in the selected MySQL database, not in the project folder.
For interactive terminals, the program uses `os.system` to run `cls` on
Windows and `clear` on other systems.

## Database Design

The database has three tables. One car can be related to many production rows
and many sales rows.

```text
cars (one) ------ (many) production
cars (one) ------ (many) sales
```

The foreign keys ensure each production and sales row refers to an existing
car. They also prevent a car from being deleted while related rows remain.

| Table | Field | MySQL type | Key or rule |
| --- | --- | --- | --- |
| `cars` | `car_id` | `INT` | Primary key, auto-increment |
| `cars` | `model` | `VARCHAR(50)` | Required, unique |
| `cars` | `price` | `DECIMAL(10,2)` | Required |
| `production` | `production_id` | `INT` | Primary key, auto-increment |
| `production` | `car_id` | `INT` | Foreign key to `cars.car_id` |
| `production` | `production_date` | `DATE` | Required |
| `production` | `quantity` | `INT` | Required |
| `sales` | `sale_id` | `INT` | Primary key, auto-increment |
| `sales` | `car_id` | `INT` | Foreign key to `cars.car_id` |
| `sales` | `sale_date` | `DATE` | Required |
| `sales` | `quantity` | `INT` | Required |

Run `DESCRIBE cars;`, `DESCRIBE production;`, and `DESCRIBE sales;` in MySQL
to see the complete server-formatted table definitions. The statements that
create these tables are in [`create_tables()`](car_company.py#L87).

## Program Logic

1. Ask for MySQL host, username, password, and database name.
2. Create the database if it does not already exist.
3. Create the three tables if they are missing.
4. Display a main menu for cars, production, sales, summary, or exit.
5. Validate values before sending them to MySQL.
6. Use parameterized SQL values for inserts, updates, and deletes.
7. Commit successful changes and roll back failed database operations.
8. Calculate cars left as total production minus total sales for each car.
9. Close the connection when the program exits.

Python connects through MySQL Connector/Python. The program creates a cursor
to execute SQL, uses `%s` placeholders for entered values, and commits or rolls
back changes. Values are passed separately from SQL, as in this insert:

```python
cursor.execute(
    "INSERT INTO cars (model, price) VALUES (%s, %s)",
    (model, price),
)
```

## SQL Concepts Demonstrated

- `CREATE DATABASE` and `CREATE TABLE` create the database structure.
- `PRIMARY KEY` and `AUTO_INCREMENT` identify rows and assign IDs.
- `NOT NULL`, `UNIQUE`, and `FOREIGN KEY` apply data constraints.
- `INSERT`, `SELECT`, `UPDATE`, and `DELETE` perform basic data operations.
- `WHERE` selects particular rows; `ORDER BY` sorts results.
- `JOIN` combines related information from tables.
- `SUM` and `GROUP BY` calculate totals for each car.

Example grouped total:

```sql
SELECT car_id, SUM(quantity)
FROM production
GROUP BY car_id;
```

This query joins production entries to cars to show each entry's model:

```sql
SELECT p.production_id, c.model, p.production_date, p.quantity
FROM production AS p
JOIN cars AS c ON c.car_id = p.car_id
ORDER BY p.production_id;
```

## Sample Run and Testing

The [README](README.md) contains example terminal runs for adding a car, recording
production and sales, and viewing the summary. Use those examples alongside
this report. Replace the sample values with the output from your own test run
before including screenshots or printouts.

The example values in the README are illustrative. Do not submit them as
evidence of a personal test run; use output from your own database instead.

| Test | Expected result | Result |
| --- | --- | --- |
| Add a valid car | Car is saved and appears in the car list. | [Pass/Fail] |
| Add production and sales | Each row appears with its car model. | [Pass/Fail] |
| Update an existing row | The selected row shows the replacement values. | [Pass/Fail] |
| Cancel a deletion | The selected row remains in the database. | [Pass/Fail] |
| Enter an invalid date or number | The program asks for valid input again. | [Pass/Fail] |
| Delete a car with linked records | MySQL prevents deletion because of the foreign key. | [Pass/Fail] |
| View the summary | Production, sales, and cars-left values match entered rows. | [Pass/Fail] |

Attach screenshots or printed output from an actual run if your teacher asks
for them. Do not present the sample transcript as a screenshot of a real run.

Run the [automated checks](tests/test_car_company.py) with
`python -m unittest discover -s tests`. The current suite passes 16 tests using
a fake database cursor; it does not replace
testing the application against a running MySQL server. Record your own manual
test results before submission.

## Limitations and Future Scope

This project demonstrates basic database operations. Its cars-left value is a
simple production-minus-sales total; negative values can appear if more sales
than production are entered. It does not enforce inventory limits, manage
staff accounts, create invoices, or provide a graphical interface. Future
improvements could include date-wise reports and user accounts with different
permissions.

## Bibliography

- Python documentation: <https://docs.python.org/3/>
- MySQL Reference Manual: <https://dev.mysql.com/doc/refman/8.0/en/>
- MySQL Connector/Python Developer Guide: <https://dev.mysql.com/doc/connector-python/en/>
- Class notes and guidance from **[Teacher name]**.