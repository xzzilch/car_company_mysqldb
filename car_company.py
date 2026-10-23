"""Menu-driven car company database project for a Class XII submission.

The program stores car details, production entries, and sales entries in MySQL.
It demonstrates related tables, primary and foreign keys, and the basic SQL
operations INSERT, SELECT, UPDATE, and DELETE. Its summary uses JOIN, SUM, and
GROUP BY to show production and sales totals for each car.

Requirements:
    - Python 3
    - MySQL Server and an account allowed to create a database and tables
    - mysql-connector-python (install with: python -m pip install mysql-connector-python)

Run with: python car_company.py

The program asks for MySQL connection settings when it starts. It creates the
selected database and missing tables automatically. Existing table data is
kept. In this file, user input is checked before it is sent to MySQL, entered
values use SQL placeholders, and each data change is committed or rolled back.
"""

from datetime import date
from decimal import Decimal, InvalidOperation
from getpass import getpass
import re
import shutil
import sys
import textwrap

import mysql.connector
from mysql.connector import Error

DATABASE_DEFAULT = "car_company"
# Fixed table details keep production and sales operations in shared functions.
RECORDS = {
    "production": ("production_id", "production_date", "Production"),
    "sales": ("sale_id", "sale_date", "Sales"),
}


def clear_screen():
    """Clear an interactive terminal without affecting redirected output."""
    if sys.stdin.isatty() and sys.stdout.isatty():
        print("\033[2J\033[H", end="")


def print_heading(title):
    """Print a simple section heading without clearing useful context."""
    divider = "-" * (len(title) + 4)
    print(f"\n{divider}\n  {title}\n{divider}")


def pause_for_menu():
    """Leave action results on screen until the user is ready to continue."""
    input("\nPress Enter to continue...")


# DATABASE SETUP
def connect_to_database():
    """Ask for MySQL settings, create the selected database, and connect."""
    print_heading("DATABASE CONNECTION")
    host = input("MySQL host [localhost]: ").strip() or "localhost"
    user = input("MySQL username [root]: ").strip() or "root"
    password = getpass("MySQL password (press Enter if none): ")
    database_prompt = f"Database name [{DATABASE_DEFAULT}]: "
    database = input(database_prompt).strip() or DATABASE_DEFAULT
    # Database names are inserted into SQL as identifiers, so allow only safe characters.
    if not re.fullmatch(r"[A-Za-z0-9_]{1,64}", database):
        raise ValueError(
            "Use a database name of 1 to 64 letters, numbers, or underscores."
        )

    settings = {"host": host, "user": user, "password": password}
    # Connect once without selecting a database so it can be created if necessary.
    server = mysql.connector.connect(**settings)
    try:
        cursor = server.cursor()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
        finally:
            cursor.close()
    finally:
        server.close()
    return mysql.connector.connect(database=database, **settings)


def create_tables(connection):
    """Create the cars, production, and sales tables when needed."""
    cursor = connection.cursor()
    try:
        # car_id is the primary key; each model must have a distinct name.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                car_id INT AUTO_INCREMENT PRIMARY KEY,
                model VARCHAR(50) NOT NULL UNIQUE,
                price DECIMAL(10, 2) NOT NULL
            )
        """)
        # car_id in these tables is a foreign key linking each entry to a car.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production (
                production_id INT AUTO_INCREMENT PRIMARY KEY,
                car_id INT NOT NULL,
                production_date DATE NOT NULL,
                quantity INT NOT NULL,
                FOREIGN KEY (car_id) REFERENCES cars(car_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INT AUTO_INCREMENT PRIMARY KEY,
                car_id INT NOT NULL,
                sale_date DATE NOT NULL,
                quantity INT NOT NULL,
                FOREIGN KEY (car_id) REFERENCES cars(car_id)
            )
        """)
        connection.commit()
    finally:
        cursor.close()


# INPUT CHECKS
def read_positive_integer(message):
    # Keep asking until the user enters a valid positive whole number.
    while True:
        try:
            value = int(input(message).strip())
            if 0 < value <= 2147483647:
                return value
        except ValueError:
            pass
        print("Enter a whole number from 1 through 2,147,483,647.")


def read_price(message):
    """Read a positive price that fits DECIMAL(10, 2)."""
    # The table allows up to eight digits before the decimal point and two after it.
    while True:
        value = input(message).strip()
        try:
            price = Decimal(value)
            has_valid_value = price.is_finite() and Decimal("0") < price
            fits_column = price <= Decimal("99999999.99")
            has_two_or_fewer_decimals = price.as_tuple().exponent >= -2
            if has_valid_value and fits_column and has_two_or_fewer_decimals:
                return price
        except InvalidOperation:
            pass
        print(
            "Enter a price over zero, up to 99,999,999.99, "
            "with at most two decimals."
        )


def read_model(message):
    """Read a non-empty model name that fits the database column."""
    while True:
        model = input(message).strip()
        if model and len(model) <= 50:
            return model
        print("Enter a model name from 1 to 50 characters long.")


def read_existing_id(message, valid_ids):
    """Accept only an ID that appeared in the list just shown to the user."""
    allowed_ids = {str(value) for value in valid_ids}
    while True:
        value = input(message).strip()
        if value in allowed_ids:
            return int(value)
        print("Choose an ID shown in the list above.")


def read_date(message, default_today=False):
    # date.fromisoformat checks that the date is a real calendar date.
    while True:
        value = input(message).strip()
        if not value and default_today:
            return date.today().isoformat()
        try:
            parsed_date = date.fromisoformat(value)
            if parsed_date.isoformat() == value:
                return value
        except ValueError:
            pass
        print("Please enter a valid date in YYYY-MM-DD format.")


def show_error_details(error):
    """Wrap database error details to fit the current terminal."""
    print("Details:")
    width = max(20, shutil.get_terminal_size((80, 24)).columns - 4)
    print(textwrap.fill(str(error), width=width))


# CAR OPERATIONS
def fetch_cars(connection):
    cursor = connection.cursor()
    try:
        # Return all rows so menus can display the same current car list.
        cursor.execute("SELECT car_id, model, price FROM cars ORDER BY car_id")
        return cursor.fetchall()
    finally:
        cursor.close()


def show_cars(connection):
    """Display all cars and return their rows for later ID selection."""
    rows = fetch_cars(connection)
    print_heading("CARS")
    if not rows:
        print("No cars found yet.")
        return rows
    for car_id, model, price in rows:
        print(f"ID {car_id} | {model} | Rs. {price}")
    return rows


def add_car(connection):
    model = read_model("Car model: ")
    price = read_price("Price (Rs.): ")
    cursor = connection.cursor()
    try:
        # %s placeholders keep entered values separate from the SQL command.
        cursor.execute(
            "INSERT INTO cars (model, price) VALUES (%s, %s)",
            (model, price),
        )
        connection.commit()
        print("Car added.")
    except Error as error:
        connection.rollback()
        print("Could not add car. The model may already exist.")
        show_error_details(error)
    finally:
        cursor.close()


def update_car(connection):
    cars = show_cars(connection)
    if not cars:
        return
    car_ids = (car[0] for car in cars)
    car_id = read_existing_id("Car ID to update: ", car_ids)
    model = read_model("New car model: ")
    price = read_price("New price (Rs.): ")
    cursor = connection.cursor()
    try:
        # WHERE with the primary key ensures only the selected car is changed.
        cursor.execute(
            "UPDATE cars SET model = %s, price = %s WHERE car_id = %s",
            (model, price, car_id),
        )
        connection.commit()
        print("Car updated." if cursor.rowcount else "No car found with that ID.")
    except Error as error:
        connection.rollback()
        print("Could not update car. Check that the model is not already used.")
        show_error_details(error)
    finally:
        cursor.close()


def confirm_delete():
    # Deletion cannot proceed unless the user explicitly enters y.
    while True:
        answer = input("Delete the selected item permanently? (y/n): ").strip().lower()
        if answer in ("y", "n"):
            return answer == "y"
        print("Please enter y or n.")


def delete_car(connection):
    cars = show_cars(connection)
    if not cars:
        return
    car_ids = (car[0] for car in cars)
    car_id = read_existing_id("Car ID to delete: ", car_ids)
    if not confirm_delete():
        print("Delete cancelled.")
        return
    cursor = connection.cursor()
    try:
        # A foreign key blocks deleting a car that still has related entries.
        cursor.execute("DELETE FROM cars WHERE car_id = %s", (car_id,))
        connection.commit()
        print("Car deleted." if cursor.rowcount else "No car found with that ID.")
    except Error as error:
        connection.rollback()
        print("Could not delete car. Remove its production and sales records first.")
        show_error_details(error)
    finally:
        cursor.close()


# PRODUCTION AND SALES OPERATIONS
def show_records(connection, table):
    """Display records from a fixed table and return rows for ID selection."""
    id_column, date_column, title = RECORDS[table]
    cursor = connection.cursor()
    try:
        # JOIN adds the readable car model to each record's stored car_id.
        cursor.execute(
            f"SELECT r.{id_column}, r.car_id, c.model, r.{date_column}, r.quantity "
            f"FROM {table} r JOIN cars c ON c.car_id = r.car_id "
            f"ORDER BY r.{id_column}"
        )
        rows = cursor.fetchall()
    finally:
        cursor.close()

    print_heading(f"{title.upper()} RECORDS")
    if not rows:
        print(f"No {table} records found yet.")
        return rows
    for record_id, car_id, model, record_date, quantity in rows:
        print(
            f"Record ID: {record_id} | Car ID: {car_id} | {model} | "
            f"Date: {record_date} | Quantity: {quantity}"
        )
    return rows


def add_record(connection, table):
    cars = show_cars(connection)
    if not cars:
        print("Add a car before recording production or sales.")
        return
    car_ids = (car[0] for car in cars)
    car_id = read_existing_id("Car ID: ", car_ids)
    record_date = read_date("Date (YYYY-MM-DD) [today]: ", default_today=True)
    quantity = read_positive_integer("Quantity: ")
    date_column = RECORDS[table][1]
    cursor = connection.cursor()
    try:
        # The values are parameterized; only fixed table/column names come from RECORDS.
        cursor.execute(
            f"INSERT INTO {table} (car_id, {date_column}, quantity) "
            "VALUES (%s, %s, %s)",
            (car_id, record_date, quantity),
        )
        connection.commit()
        print("Record added.")
    except Error as error:
        connection.rollback()
        print("Could not add record. Check the car ID and date.")
        show_error_details(error)
    finally:
        cursor.close()


def update_record(connection, table):
    records = show_records(connection, table)
    if not records:
        return
    id_column, date_column, _ = RECORDS[table]
    record_ids = (record[0] for record in records)
    record_id = read_existing_id("Record ID to update: ", record_ids)
    cars = show_cars(connection)
    if not cars:
        return
    car_ids = (car[0] for car in cars)
    car_id = read_existing_id("Choose the new car ID: ", car_ids)
    record_date = read_date("New date (YYYY-MM-DD): ")
    quantity = read_positive_integer("New quantity: ")

    cursor = connection.cursor()
    try:
        # Update all fields of the chosen row using its primary-key ID.
        cursor.execute(
            f"UPDATE {table} SET car_id = %s, {date_column} = %s, quantity = %s "
            f"WHERE {id_column} = %s",
            (car_id, record_date, quantity, record_id),
        )
        connection.commit()
        print("Record updated." if cursor.rowcount else "No record found with that ID.")
    except Error as error:
        connection.rollback()
        print("Could not update record. Check the car ID and date.")
        show_error_details(error)
    finally:
        cursor.close()


def delete_record(connection, table):
    records = show_records(connection, table)
    if not records:
        return
    id_column = RECORDS[table][0]
    record_ids = (record[0] for record in records)
    record_id = read_existing_id("Record ID to delete: ", record_ids)
    if not confirm_delete():
        print("Delete cancelled.")
        return
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"DELETE FROM {table} WHERE {id_column} = %s",
            (record_id,),
        )
        connection.commit()
        print("Record deleted." if cursor.rowcount else "No record found with that ID.")
    except Error as error:
        connection.rollback()
        print("Could not delete record.")
        show_error_details(error)
    finally:
        cursor.close()


# SUMMARY REPORT
def get_totals(connection, table):
    cursor = connection.cursor()
    try:
        # GROUP BY makes one total for each car instead of one overall total.
        cursor.execute(
            f"SELECT car_id, SUM(quantity) FROM {table} GROUP BY car_id"
        )
        return dict(cursor.fetchall())
    finally:
        cursor.close()


def show_summary(connection):
    cars = fetch_cars(connection)
    print_heading("PRODUCTION AND SALES SUMMARY")
    if not cars:
        print("No cars found yet.")
        return
    produced = get_totals(connection, "production")
    sold = get_totals(connection, "sales")
    for car_id, model, _ in cars:
        # A car without entries is still shown, with its missing total displayed as zero.
        print(
            f"{model} | Produced {produced.get(car_id, 0)} | "
            f"Sold {sold.get(car_id, 0)}"
        )


# MENU AND PROGRAM FLOW
def manage_cars(connection):
    # Menu choices map directly to the operation they run.
    actions = {
        "1": show_cars,
        "2": add_car,
        "3": update_car,
        "4": delete_car,
    }
    while True:
        clear_screen()
        print_heading("CARS MENU")
        print("1 View | 2 Add | 3 Update | 4 Delete | 0 Back")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            return
        action = actions.get(choice)
        if action:
            action(connection)
            pause_for_menu()
        else:
            print("Choose 1, 2, 3, 4, or 0.")
            pause_for_menu()


def manage_records(connection, table):
    title = RECORDS[table][2].upper()
    while True:
        clear_screen()
        print_heading(f"{title} MENU")
        print("1 View | 2 Add | 3 Update | 4 Delete | 0 Back")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            return
        if choice == "1":
            show_records(connection, table)
        elif choice == "2":
            add_record(connection, table)
        elif choice == "3":
            update_record(connection, table)
        elif choice == "4":
            delete_record(connection, table)
        else:
            print("Choose 1, 2, 3, 4, or 0.")
        pause_for_menu()


def main():
    connection = None
    try:
        connection = connect_to_database()
        # Create missing tables on every start; existing data is left unchanged.
        create_tables(connection)
    except (Error, ValueError) as error:
        print("Could not start the database project.")
        show_error_details(error)
        print(
            "Check the MySQL settings, connector installation, "
            "and database permissions."
        )
        if connection is not None:
            try:
                connection.close()
            except Error:
                pass
        return
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")
        if connection is not None:
            try:
                connection.close()
            except Error:
                pass
        return

    try:
        while True:
            clear_screen()
            print_heading("MAIN MENU")
            print("1 Cars | 2 Production | 3 Sales")
            print("4 Summary | 0 Exit")
            choice = input("Choose an option: ").strip()
            try:
                if choice == "1":
                    manage_cars(connection)
                elif choice == "2":
                    manage_records(connection, "production")
                elif choice == "3":
                    manage_records(connection, "sales")
                elif choice == "4":
                    show_summary(connection)
                    pause_for_menu()
                elif choice == "0":
                    print("Goodbye.")
                    break
                else:
                    print("Choose 1, 2, 3, 4, or 0.")
                    pause_for_menu()
            except Error as error:
                # A failed query returns the user to the menu instead of ending the program.
                print("Database operation failed.")
                show_error_details(error)
                try:
                    connection.rollback()
                except Error:
                    print("The database connection was lost. Exiting the program.")
                    break
                pause_for_menu()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")
    finally:
        if connection is not None:
            try:
                if connection.is_connected():
                    connection.close()
            except Error:
                print("Could not close the database connection cleanly.")


if __name__ == "__main__":
    main()
