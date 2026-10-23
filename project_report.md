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
| Sample Run and Testing | [Page] |
| Limitations and Future Scope | [Page] |
| Bibliography | [Page] |

Update page numbers after arranging or printing the final report.

## Project Overview

The Car Company Database Management System is a menu-driven Python program
connected to a MySQL database. It stores car models and prices and records
production and sales quantities by date. The program can display, add, update,
and delete records, and show total production and sales for each car model.

The program creates the selected database and any missing tables when it
starts. The user supplies connection details and enters project data through
the menus instead of changing variables in the source code.

## Objectives

- Store data in related MySQL tables.
- Use primary keys and foreign keys to identify and relate rows.
- Perform insert, display, update, and delete operations.
- Use a join to display record details with a car model.
- Use `SUM` and `GROUP BY` to calculate totals for each car.
- Validate user input and handle common database errors.

## Requirements

### Hardware

- Computer capable of running Python and MySQL Server.
- Keyboard and display for the command-line interface.

### Software

- Python 3.
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

## Database Design

The database has three tables. One car can be related to many production rows
and many sales rows.

```text
cars (one) ------ (many) production
cars (one) ------ (many) sales
```

| Table | Important fields |
| --- | --- |
| `cars` | `car_id` primary key, `model` unique model name, `price` decimal price. |
| `production` | `production_id` primary key, `car_id` foreign key, `production_date`, `quantity`. |
| `sales` | `sale_id` primary key, `car_id` foreign key, `sale_date`, `quantity`. |

The foreign keys ensure each production and sales row refers to an existing
car. They also prevent a car from being deleted while related rows remain.

## Program Logic

1. Ask for MySQL host, username, password, and database name.
2. Create the database if it does not already exist.
3. Create the three tables if they are missing.
4. Display a main menu for cars, production, sales, summary, or exit.
5. Validate values before sending them to MySQL.
6. Use parameterized SQL values for inserts, updates, and deletes.
7. Commit successful changes and roll back failed database operations.
8. Close the connection when the program exits.

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

## Sample Run and Testing

The README contains example terminal runs for adding a car, recording
production and sales, and viewing the summary. Use those examples alongside
this report. Replace the sample values with the output from your own test run
before including screenshots or printouts.

| Test | Expected result | Result |
| --- | --- | --- |
| Add a valid car | Car is saved and appears in the car list. | [Pass/Fail] |
| Add production and sales | Each row appears with its car model. | [Pass/Fail] |
| Update an existing row | The selected row shows the replacement values. | [Pass/Fail] |
| Cancel a deletion | The selected row remains in the database. | [Pass/Fail] |
| Enter an invalid date or number | The program asks for valid input again. | [Pass/Fail] |
| Delete a car with linked records | MySQL prevents deletion because of the foreign key. | [Pass/Fail] |
| View the summary | Production and sales totals match entered rows. | [Pass/Fail] |

Attach screenshots or printed output from an actual run if your teacher asks
for them. Do not present the sample transcript as a screenshot of a real run.

## Limitations and Future Scope

This project demonstrates basic database operations. It does not calculate
live inventory, manage staff accounts, create invoices, or provide a graphical
interface. Future improvements could include date-wise reports, stock
calculation, and user accounts with different permissions.

## Bibliography

- Python documentation: <https://docs.python.org/3/>
- MySQL Reference Manual: <https://dev.mysql.com/doc/refman/8.0/en/>
- MySQL Connector/Python Developer Guide: <https://dev.mysql.com/doc/connector-python/en/>
- Class notes and guidance from **[Teacher name]**.