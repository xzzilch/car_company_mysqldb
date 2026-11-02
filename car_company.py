"""Menu-driven car company database project for a Class XII submission.

The program stores car details, production entries, and sales entries in MySQL.
It demonstrates related tables, primary and foreign keys, and the basic SQL
operations INSERT, SELECT, UPDATE, and DELETE. It uses JOIN to display record
details with car names and SUM with GROUP BY to calculate per-car totals.

Requirements:
    - Python 3
    - MySQL Server and an account allowed to create a database and tables
    - mysql-connector-python (install with: python -m pip install mysql-connector-python)

Run with: python car_company.py

The program asks for MySQL connection settings when it starts. It creates the
selected database and missing tables automatically. Existing table data is
kept. In this file, user input is checked before it is sent to MySQL, entered
values use SQL placeholders, and each successful data-changing statement is
committed immediately through autocommit. Rollback is attempted after errors,
but cannot undo a statement MySQL has already committed.
"""

from datetime import date
from decimal import Decimal, InvalidOperation
from getpass import getpass
import os
import re
import shutil
import sys
import textwrap
import unicodedata

import mysql.connector
from mysql.connector import Error

class DatabaseRollbackError(Error):
    """Signal that a rollback failed after its details were already reported."""


DATABASE_DEFAULT = "car_company"
EARLIEST_MODEL_YEAR = 1886
MODEL_YEAR_FUTURE_LIMIT = 2
# Fixed table details keep production and sales operations in shared functions.
RECORDS = {
    "production": ("production_id", "production_date", "Production"),
    "sales": ("sale_id", "sale_date", "Sales"),
}
RECORD_DATE_LABELS = {
    "production": "Production date",
    "sales": "Sale date",
}
RECORD_COLUMNS = {
    "production": {
        "shift": "VARCHAR(20) NOT NULL DEFAULT 'Day'",
        "quality_checked": "BOOLEAN NOT NULL DEFAULT FALSE",
    },
    "sales": {
        "sales_channel": "VARCHAR(30) NOT NULL DEFAULT 'Other'",
        "payment_method": "VARCHAR(20) NOT NULL DEFAULT 'Other'",
        "warranty_months": "SMALLINT UNSIGNED NOT NULL DEFAULT 0",
    },
}
CAR_COLUMNS = {
    "manufacturer": "VARCHAR(50) NOT NULL DEFAULT 'Unknown'",
    "model_year": "SMALLINT UNSIGNED NOT NULL DEFAULT 2000",
    "color": "VARCHAR(30) NOT NULL DEFAULT 'Unknown'",
    "is_electric": "BOOLEAN NOT NULL DEFAULT FALSE",
}


def clear_screen():
    """Clear an interactive terminal without affecting redirected output."""
    if sys.stdin.isatty() and sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def print_heading(title):
    """Print a compact, terminal-width-aware section heading."""
    width = max(10, shutil.get_terminal_size((80, 24)).columns - 2)
    title = title if len(title) <= width - 4 else f"{title[:width - 7]}..."
    divider = "=" * (width - 2)
    print(f"\n+{divider}+")
    print(f"| {title:^{width - 4}} |")
    print(f"+{divider}+")


def read_input(message, separator=False):
    """Show a consistent prompt, optionally separating major menu choices."""
    if separator:
        width = min(40, max(1, shutil.get_terminal_size((80, 24)).columns - 4))
        print(f"\n  {'_' * width}")
    return input(f"  > {message}")


def visible_text(value):
    """Escape control characters so stored text cannot disrupt terminal output."""
    return "".join(
        character if character.isprintable() else ascii(character)[1:-1]
        for character in str(value)
    )


def display_width(value):
    """Estimate terminal cell width for ordinary and East Asian text."""
    width = 0
    for character in value:
        if unicodedata.combining(character):
            continue
        width += 2 if unicodedata.east_asian_width(character) in ("F", "W") else 1
    return width


def fit_cell(value, width):
    """Truncate text to a terminal-cell width without splitting wide characters."""
    if display_width(value) <= width:
        return value
    suffix = "..." if width >= 3 else ""
    available_width = width - display_width(suffix)
    clipped = []
    current_width = 0
    for character in value:
        character_width = display_width(character)
        if current_width + character_width > available_width:
            break
        clipped.append(character)
        current_width += character_width
    return "".join(clipped) + suffix


def print_table(headers, rows, max_widths=None, alignments=None):
    """Print a compact table that shrinks to fit the current terminal."""
    headers = tuple(visible_text(header) for header in headers)
    if not headers:
        return
    rows = [tuple(visible_text(value) for value in row) for row in rows]
    if any(len(row) != len(headers) for row in rows):
        raise ValueError("Each table row must have the same number of cells as headers.")
    if max_widths is not None and len(max_widths) != len(headers):
        raise ValueError("max_widths must have one entry per table column.")
    if max_widths is not None and any(
        width is not None
        and (not isinstance(width, int) or isinstance(width, bool) or width < 1)
        for width in max_widths
    ):
        raise ValueError("Column widths must be positive integers or None.")
    if alignments is not None and len(alignments) != len(headers):
        raise ValueError("alignments must have one entry per table column.")
    if alignments is not None and any(
        alignment not in ("<", ">") for alignment in alignments
    ):
        raise ValueError("Column alignments must be '<' or '>'.")

    widths = [
        max(
            [display_width(header)]
            + [display_width(row[index]) for row in rows]
        )
        for index, header in enumerate(headers)
    ]
    if max_widths:
        widths = [
            min(width, max_widths[index])
            if max_widths[index] is not None
            else width
            for index, width in enumerate(widths)
        ]

    terminal_width = max(8, shutil.get_terminal_size((80, 24)).columns - 4)
    while sum(widths) + 3 * (len(widths) - 1) > terminal_width:
        candidates = [index for index, width in enumerate(widths) if width > 1]
        if not candidates:
            break
        widest = max(candidates, key=widths.__getitem__)
        widths[widest] -= 1

    alignments = alignments or ("<",) * len(headers)

    def cell(value, width, alignment):
        value = fit_cell(value, width)
        padding = max(0, width - display_width(value))
        return value + (" " * padding) if alignment == "<" else (" " * padding) + value

    def format_row(values):
        return " | ".join(
            cell(value, width, alignment)
            for value, width, alignment in zip(values, widths, alignments)
        )

    print(format_row(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(format_row(row))


def pause_for_menu():
    """Leave action results on screen until the user is ready to continue."""
    read_input("Press Enter to continue...")


def close_connection(connection):
    """Close a connection and report cleanup errors instead of hiding them."""
    try:
        connection.close()
    except Error as error:
        print("Could not close the database connection cleanly.")
        show_error_details(error)


# DATABASE SETUP
def connect_to_database():
    """Ask for MySQL settings, create the selected database, and connect."""
    print_heading("DATABASE CONNECTION")
    host = read_input("MySQL host [localhost]: ").strip() or "localhost"
    user = read_input("MySQL username [root]: ").strip() or "root"
    print("  > MySQL password (input hidden; press Enter if none)")
    password = getpass("  > ")
    database_prompt = f"Database name [{DATABASE_DEFAULT}]: "
    database = read_input(database_prompt).strip() or DATABASE_DEFAULT
    # Database names are inserted into SQL as identifiers, so allow only safe characters.
    if not re.fullmatch(r"[A-Za-z0-9_]{1,64}", database):
        raise ValueError(
            "Use a database name of 1 to 64 letters, numbers, or underscores."
        )

    # A timeout avoids a long hang when the host is unreachable.
    settings = {
        "host": host,
        "user": user,
        "password": password,
        "connection_timeout": 10,
    }
    # Connect once without selecting a database so it can be created if necessary.
    server = mysql.connector.connect(**settings)
    try:
        cursor = server.cursor()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
        finally:
            close_cursor(cursor)
    finally:
        close_connection(server)
    connection = mysql.connector.connect(database=database, **settings)
    # The connector disables autocommit by default, so read-only menus would
    # hold one transaction open and keep seeing a stale snapshot of other
    # sessions' writes. Autocommit keeps every SELECT current.
    try:
        connection.autocommit = True
    except Error:
        close_connection(connection)
        raise
    return connection


def create_tables(connection):
    """Create the cars, production, and sales tables when needed."""
    cursor = connection.cursor()
    try:
        # car_id is the primary key; each model must have a distinct name.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                car_id INT AUTO_INCREMENT PRIMARY KEY,
                model VARCHAR(50) NOT NULL UNIQUE,
                price DECIMAL(10, 2) NOT NULL,
                manufacturer VARCHAR(50) NOT NULL DEFAULT 'Unknown',
                model_year SMALLINT UNSIGNED NOT NULL DEFAULT 2000,
                color VARCHAR(30) NOT NULL DEFAULT 'Unknown',
                is_electric BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)
        # car_id in these tables is a foreign key linking each entry to a car.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS production (
                production_id INT AUTO_INCREMENT PRIMARY KEY,
                car_id INT NOT NULL,
                production_date DATE NOT NULL,
                quantity INT NOT NULL,
                shift VARCHAR(20) NOT NULL DEFAULT 'Day',
                quality_checked BOOLEAN NOT NULL DEFAULT FALSE,
                FOREIGN KEY (car_id) REFERENCES cars(car_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INT AUTO_INCREMENT PRIMARY KEY,
                car_id INT NOT NULL,
                sale_date DATE NOT NULL,
                quantity INT NOT NULL,
                sales_channel VARCHAR(30) NOT NULL DEFAULT 'Other',
                payment_method VARCHAR(20) NOT NULL DEFAULT 'Other',
                warranty_months SMALLINT UNSIGNED NOT NULL DEFAULT 0,
                FOREIGN KEY (car_id) REFERENCES cars(car_id)
            )
        """)
        # CREATE TABLE IF NOT EXISTS does not add fields to existing databases.
        for table, columns in (
            ("cars", CAR_COLUMNS),
            ("production", RECORD_COLUMNS["production"]),
            ("sales", RECORD_COLUMNS["sales"]),
        ):
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            existing_columns = {column[0] for column in cursor.fetchall()}
            for column, definition in columns.items():
                if column not in existing_columns:
                    try:
                        cursor.execute(
                            f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}"
                        )
                    except Error as error:
                        if error.errno != 1060:
                            raise
        connection.commit()
    finally:
        close_cursor(cursor)


# INPUT CHECKS
def read_positive_integer(message):
    # Keep asking until the user enters a valid positive whole number.
    # Digits only: int() also accepts underscores and a plus sign, which the
    # prompt never advertises.
    while True:
        raw = read_input(message).strip()
        if re.fullmatch(r"[0-9]{1,10}", raw):
            value = int(raw)
            if 0 < value <= 2147483647:
                return value
        print("Enter a whole number from 1 through 2,147,483,647.")


def read_integer_range(message, minimum, maximum):
    """Read an integer that fits a specific database column range."""
    while True:
        raw = read_input(message).strip()
        if re.fullmatch(r"[0-9]{1,5}", raw):
            value = int(raw)
            if minimum <= value <= maximum:
                return value
        print(f"Enter a whole number from {minimum} through {maximum}.")


def read_text(message, field_name, max_length):
    """Read a non-empty string that fits a VARCHAR field."""
    while True:
        value = read_input(message).strip()
        if value and len(value) <= max_length and value.isprintable():
            return value
        print(
            f"Enter {field_name} using 1 to {max_length} printable characters."
        )


def read_yes_no(message):
    """Read an explicit yes/no answer for a BOOLEAN field."""
    while True:
        value = read_input(message).strip().lower()
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        print("Enter y or n.")


def read_price(message):
    """Read a positive price that fits DECIMAL(10, 2)."""
    # The table allows up to eight digits before the decimal point and two after it.
    price_pattern = r"(?:[0-9]{1,64}(?:\.[0-9]{0,2})?|\.[0-9]{1,2})"
    while True:
        value = read_input(message).strip()
        if not re.fullmatch(price_pattern, value):
            print(
                "Enter a price greater than zero, up to 99,999,999.99, "
                "with at most two decimals."
            )
            continue
        try:
            price = Decimal(value)
        except InvalidOperation:
            price = None
        if (price is not None and price.is_finite()
                and Decimal("0") < price
                and price <= Decimal("99999999.99")
                and price.as_tuple().exponent >= -2):
            return price
        print(
            "Enter a price greater than zero, up to 99,999,999.99, "
            "with at most two decimals."
        )

def read_model(message):
    """Read a non-empty model name that fits the database column."""
    while True:
        model = read_input(message).strip()
        if model and len(model) <= 50 and model.isprintable():
            return model
        print("Enter a model name using 1 to 50 printable characters.")


def read_car_details(is_update=False):
    """Collect and validate all editable car fields."""
    prefix = "New " if is_update else ""
    latest_model_year = date.today().year + MODEL_YEAR_FUTURE_LIMIT
    return (
        read_model(f"{prefix}car model: "),
        read_price(f"{prefix}price (Rs.): "),
        read_text(f"{prefix}manufacturer: ", "a manufacturer", 50),
        read_integer_range(
            f"{prefix}model year ({EARLIEST_MODEL_YEAR}-{latest_model_year}): ",
            EARLIEST_MODEL_YEAR,
            latest_model_year,
        ),
        read_text(f"{prefix}color: ", "a color", 30),
        read_yes_no(f"{prefix}electric? (y/n): "),
    )


def get_record_config(table):
    """Return fixed SQL metadata, rejecting unrecognized table names."""
    if table not in RECORDS:
        raise ValueError(f"Unsupported record table: {table}")
    return RECORDS[table]


def read_record_details(table):
    """Collect the validated fields that differ between production and sales."""
    if table == "production":
        return (
            read_text("Production shift: ", "a shift", 20),
            read_yes_no("Quality checked? (y/n): "),
        )
    if table == "sales":
        return (
            read_text("Sales channel: ", "a sales channel", 30),
            read_text("Payment method: ", "a payment method", 20),
            read_integer_range("Warranty months (0-65535): ", 0, 65535),
        )
    raise ValueError(f"Unsupported record table: {table}")


def read_existing_id(message, valid_ids):
    """Accept only an ID that appeared in the list just shown to the user."""
    allowed_ids = {str(value) for value in valid_ids}
    while True:
        value = read_input(message).strip()
        if value in allowed_ids:
            return int(value)
        print("Choose an ID shown in the list above.")


def read_date(message, default_today=False):
    # MySQL DATE supports 1000-01-01 through 9999-12-31.
    while True:
        value = read_input(message).strip()
        if not value and default_today:
            return date.today().isoformat()
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            print(
                "Enter a valid date in YYYY-MM-DD format, from "
                "1000-01-01 through 9999-12-31."
            )
            continue
        try:
            parsed_date = date.fromisoformat(value)
        except ValueError:
            parsed_date = None
        if (
            parsed_date is not None
            and date(1000, 1, 1) <= parsed_date <= date(9999, 12, 31)
        ):
            return value
        print(
            "Enter a valid date in YYYY-MM-DD format, from "
            "1000-01-01 through 9999-12-31."
        )


def show_error_details(error):
    """Wrap database error details to fit the current terminal."""
    print("Details:")
    width = max(20, shutil.get_terminal_size((80, 24)).columns - 4)
    print(textwrap.fill(visible_text(error), width=width))


def report_database_error(connection, error, message):
    """Show the original database failure and report any rollback failure."""
    print(message)
    show_error_details(error)
    try:
        connection.rollback()
    except Error as rollback_error:
        print("Could not roll back the failed database operation.")
        show_error_details(rollback_error)
        raise DatabaseRollbackError(str(rollback_error)) from rollback_error


def close_cursor(cursor):
    """Close a cursor without hiding a database cleanup failure."""
    try:
        cursor.close()
    except Error as error:
        print("Could not close the database cursor cleanly.")
        show_error_details(error)


# CAR OPERATIONS
def fetch_cars(connection):
    cursor = connection.cursor()
    try:
        # Return all rows so menus can display the same current car list.
        cursor.execute(
            "SELECT car_id, model, price, manufacturer, model_year, color, "
            "is_electric FROM cars ORDER BY car_id"
        )
        return cursor.fetchall()
    finally:
        close_cursor(cursor)


def show_cars(connection):
    """Display all cars and return their rows for later ID selection."""
    rows = fetch_cars(connection)
    print_heading("CARS")
    if not rows:
        print("No cars found yet.")
        return rows
    table_rows = []
    for row in rows:
        car_id, model, price, manufacturer, model_year, color, is_electric = row
        table_rows.append(
            (
                car_id,
                model,
                f"Rs. {price}",
                manufacturer,
                model_year,
                color,
                "Yes" if is_electric else "No",
            )
        )
    print_table(
        ("ID", "Model", "Price", "Manufacturer", "Year", "Color", "Electric"),
        table_rows,
        max_widths=(6, 24, 16, 20, 6, 14, 8),
        alignments=(">", "<", ">", "<", ">", "<", "<"),
    )
    return rows


def add_car(connection):
    model, price, manufacturer, model_year, color, is_electric = read_car_details()
    cursor = connection.cursor()
    try:
        # %s placeholders keep entered values separate from the SQL command.
        cursor.execute(
            "INSERT INTO cars "
            "(model, price, manufacturer, model_year, color, is_electric) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (model, price, manufacturer, model_year, color, is_electric),
        )
        connection.commit()
        print("Car added successfully.")
    except Error as error:
        report_database_error(
            connection, error, "Could not add car. Review the database error below."
        )
    finally:
        close_cursor(cursor)


def update_car(connection):
    cars = show_cars(connection)
    if not cars:
        return
    car_ids = (car[0] for car in cars)
    car_id = read_existing_id("Car ID to update: ", car_ids)
    model, price, manufacturer, model_year, color, is_electric = read_car_details(
        is_update=True
    )
    cursor = connection.cursor()
    try:
        # WHERE with the primary key ensures only the selected car is changed.
        cursor.execute(
            "UPDATE cars SET model = %s, price = %s, manufacturer = %s, "
            "model_year = %s, color = %s, is_electric = %s WHERE car_id = %s",
            (model, price, manufacturer, model_year, color, is_electric, car_id),
        )
        connection.commit()
        report_update_result(
            cursor,
            "cars",
            "car_id",
            car_id,
            "Car updated successfully.",
            "No changes needed.",
            "No car found with that ID.",
        )
    except Error as error:
        report_database_error(
            connection,
            error,
            "Could not update car. Review the database error below.",
        )
    finally:
        close_cursor(cursor)


def confirm_delete():
    # Deletion cannot proceed unless the user explicitly enters y.
    while True:
        answer = read_input(
            "Delete the selected item permanently? (y/n): "
        ).strip().lower()
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
        print("Deletion cancelled.")
        return
    cursor = connection.cursor()
    try:
        # A foreign key blocks deleting a car that still has related entries.
        cursor.execute("DELETE FROM cars WHERE car_id = %s", (car_id,))
        connection.commit()
        print(
            "Car deleted successfully."
            if cursor.rowcount
            else "No car found with that ID."
        )
    except Error as error:
        report_database_error(
            connection,
            error,
            "Could not delete car. Remove its production and sales records first.",
        )
    finally:
        close_cursor(cursor)


# PRODUCTION AND SALES OPERATIONS
def show_records(connection, table):
    """Display records from a fixed table and return rows for ID selection."""
    id_column, date_column, title = get_record_config(table)
    extra_columns = tuple(RECORD_COLUMNS[table])
    cursor = connection.cursor()
    try:
        # JOIN adds the readable car model to each record's stored car_id.
        cursor.execute(
            f"SELECT r.{id_column}, r.car_id, c.model, r.{date_column}, "
            f"r.quantity, {', '.join(f'r.{column}' for column in extra_columns)} "
            f"FROM {table} r JOIN cars c ON c.car_id = r.car_id "
            f"ORDER BY r.{id_column}"
        )
        rows = cursor.fetchall()
    finally:
        close_cursor(cursor)

    print_heading(f"{title.upper()} RECORDS")
    if not rows:
        print(f"No {table} records found yet.")
        return rows
    display_rows = []
    for row in rows:
        record_id, car_id, model, record_date, quantity, *extra_values = row
        display_values = []
        for column, value in zip(extra_columns, extra_values):
            if column in ("quality_checked", "is_electric"):
                value = "Yes" if value else "No"
            display_values.append(value)
        display_rows.append(
            (record_id, car_id, model, record_date, quantity, *display_values)
        )
    extra_headers = {
        "shift": "Shift",
        "quality_checked": "Quality?",
        "sales_channel": "Channel",
        "payment_method": "Payment",
        "warranty_months": "Warranty",
    }
    print_table(
        (
            "ID",
            "Car ID",
            "Model",
            "Date",
            "Qty",
            *(extra_headers[column] for column in extra_columns),
        ),
        display_rows,
        max_widths=(
            6,
            7,
            22,
            10,
            8,
            *(max(12, len(extra_headers[column]) + 1) for column in extra_columns),
        ),
        alignments=(">", ">", "<", "<", ">", *("<" for _ in extra_columns)),
    )
    return rows


def add_record(connection, table):
    id_column, date_column, record_title = get_record_config(table)
    extra_columns = tuple(RECORD_COLUMNS[table])
    cars = show_cars(connection)
    if not cars:
        print("Add a car before recording production or sales.")
        return
    car_ids = (car[0] for car in cars)
    car_id = read_existing_id("Car ID: ", car_ids)
    date_label = RECORD_DATE_LABELS[table]
    record_date = read_date(
        f"{date_label} (YYYY-MM-DD, future dates allowed) [today]: ",
        default_today=True,
    )
    quantity = read_positive_integer("Quantity: ")
    extra_values = read_record_details(table)
    columns = ("car_id", date_column, "quantity", *extra_columns)
    placeholders = ", ".join(["%s"] * len(columns))
    values = (car_id, record_date, quantity, *extra_values)
    cursor = connection.cursor()
    try:
        # The values are parameterized; only fixed table/column names come from RECORDS.
        cursor.execute(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            values,
        )
        connection.commit()
        print(f"{record_title} record added successfully.")
    except Error as error:
        report_database_error(
            connection,
            error,
            f"Could not add the {record_title.lower()} record. "
            "Review the database error below.",
        )
    finally:
        close_cursor(cursor)


def update_record(connection, table):
    id_column, date_column, record_title = get_record_config(table)
    extra_columns = tuple(RECORD_COLUMNS[table])
    records = show_records(connection, table)
    if not records:
        return
    record_ids = (record[0] for record in records)
    record_id = read_existing_id("Record ID to update: ", record_ids)
    cars = show_cars(connection)
    if not cars:
        return
    car_ids = (car[0] for car in cars)
    car_id = read_existing_id("Choose the new car ID: ", car_ids)
    date_label = RECORD_DATE_LABELS[table]
    record_date = read_date(
        f"New {date_label.lower()} (YYYY-MM-DD, future dates allowed): "
    )
    quantity = read_positive_integer("New quantity: ")
    extra_values = read_record_details(table)

    cursor = connection.cursor()
    try:
        # Update all fields of the chosen row using its primary-key ID.
        assignments = [
            "car_id = %s",
            f"{date_column} = %s",
            "quantity = %s",
            *(f"{column} = %s" for column in extra_columns),
        ]
        cursor.execute(
            f"UPDATE {table} SET {', '.join(assignments)} "
            f"WHERE {id_column} = %s",
            (car_id, record_date, quantity, *extra_values, record_id),
        )
        connection.commit()
        report_update_result(
            cursor,
            table,
            id_column,
            record_id,
            f"{record_title} record updated successfully.",
            "No changes needed.",
            f"No {record_title.lower()} record found with that ID.",
        )
    except Error as error:
        report_database_error(
            connection,
            error,
            f"Could not update the {record_title.lower()} record. "
            "Review the database error below.",
        )
    finally:
        close_cursor(cursor)


def delete_record(connection, table):
    id_column, _, record_title = get_record_config(table)
    records = show_records(connection, table)
    if not records:
        return
    record_ids = (record[0] for record in records)
    record_id = read_existing_id("Record ID to delete: ", record_ids)
    if not confirm_delete():
        print("Deletion cancelled.")
        return
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"DELETE FROM {table} WHERE {id_column} = %s",
            (record_id,),
        )
        connection.commit()
        print(
            f"{record_title} record deleted successfully."
            if cursor.rowcount
            else f"No {record_title.lower()} record found with that ID."
        )
    except Error as error:
        report_database_error(
            connection,
            error,
            f"Could not delete the {record_title.lower()} record. "
            "Review the database error below.",
        )
    finally:
        close_cursor(cursor)


# SUMMARY REPORT
def get_totals(connection, table, as_of=None):
    _, date_column, _ = get_record_config(table)
    as_of = date.today() if as_of is None else as_of
    cursor = connection.cursor()
    try:
        # Exclude future-dated plans from current production and sales totals.
        cursor.execute(
            f"SELECT car_id, SUM(quantity) FROM {table} "
            f"WHERE {date_column} <= %s GROUP BY car_id",
            (as_of,),
        )
        return dict(cursor.fetchall())
    finally:
        close_cursor(cursor)


def show_summary(connection):
    as_of = date.today()
    cars = fetch_cars(connection)
    print_heading("PRODUCTION AND SALES SUMMARY")
    print(f"  Totals through {as_of.isoformat()} (future-dated entries excluded)")
    if not cars:
        print("No cars found yet.")
        return
    produced = get_totals(connection, "production", as_of)
    sold = get_totals(connection, "sales", as_of)
    model_width = 30
    summary_rows = []
    negative_stock_rows = []
    for car in cars:
        car_id, model = car[0], car[1]
        # A car without entries is still shown, with its missing total displayed as zero.
        produced_count = produced.get(car_id, 0)
        sold_count = sold.get(car_id, 0)
        left_count = produced_count - sold_count
        display_model = (
            model if len(model) <= model_width else f"{model[:model_width - 3]}..."
        )
        summary_rows.append((display_model, produced_count, sold_count, left_count))
        if left_count < 0:
            negative_stock_rows.append((display_model, abs(left_count)))

    print_table(
        ("Car model", "Produced", "Sold", "Cars left"),
        summary_rows,
        max_widths=(model_width, None, None, None),
        alignments=("<", ">", ">", ">"),
    )
    if negative_stock_rows:
        print("\nWARNING: Sales exceed recorded production for:")
        print_table(
            ("Car model", "Shortfall"),
            negative_stock_rows,
            max_widths=(model_width, None),
            alignments=("<", ">"),
        )


# MENU AND PROGRAM FLOW
def manage_cars(connection):
    actions = {
        "1": show_cars,
        "2": add_car,
        "3": update_car,
        "4": delete_car,
    }
    while True:
        clear_screen()
        print_heading("CAR MANAGEMENT")
        print("  1  View cars")
        print("  2  Add a car")
        print("  3  Update a car")
        print("  4  Delete a car")
        print("  0  Back to main menu")
        choice = read_input("Choose an option: ", separator=True).strip()
        if choice == "0":
            return
        action = actions.get(choice)
        if action:
            action(connection)
        else:
            print("Invalid option. Enter 1, 2, 3, 4, or 0.")
        pause_for_menu()


def manage_records(connection, table):
    _, _, record_title = get_record_config(table)
    title = record_title.upper()
    while True:
        clear_screen()
        print_heading(f"{title} MANAGEMENT")
        print(f"  1  View {title.lower()} records")
        print(f"  2  Add a {title.lower()} record")
        print(f"  3  Update a {title.lower()} record")
        print(f"  4  Delete a {title.lower()} record")
        print("  0  Back to main menu")
        choice = read_input("Choose an option: ", separator=True).strip()
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
            print("Invalid option. Enter 1, 2, 3, 4, or 0.")
        pause_for_menu()


def report_update_result(
    cursor,
    table,
    id_column,
    item_id,
    updated_message,
    unchanged_message,
    missing_message,
):
    """Distinguish a missing row from a successful no-op update."""
    if cursor.rowcount:
        print(updated_message)
        return

    # MySQL can report zero changed rows when the matching row already had these values.
    cursor.execute(
        f"SELECT 1 FROM {table} WHERE {id_column} = %s",
        (item_id,),
    )
    print(unchanged_message if cursor.fetchone() else missing_message)


def main():
    connection = None
    try:
        connection = connect_to_database()
        # Create missing tables on every start; existing data is left unchanged.
        create_tables(connection)
    except (Error, ValueError) as error:
        print("Database setup failed; the application could not start.")
        show_error_details(error)
        print(
            "Check the MySQL settings, connector installation, "
            "and database permissions."
        )
        if connection is not None:
            close_connection(connection)
        return
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")
        if connection is not None:
            close_connection(connection)
        return

    try:
        while True:
            clear_screen()
            print_heading("CAR COMPANY DATABASE")
            print("  1  Manage cars")
            print("  2  Manage production")
            print("  3  Manage sales")
            print("  4  View production and sales summary")
            print("  0  Exit")
            choice = read_input("Choose an option: ", separator=True).strip()
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
                    print("Invalid option. Enter 1, 2, 3, 4, or 0.")
                    pause_for_menu()
            except DatabaseRollbackError:
                print("The database connection was lost. Exiting the program.")
                break
            except Error as error:
                # A failed query returns the user to the menu instead of ending the program.
                print("A database operation failed.")
                show_error_details(error)
                try:
                    connection.rollback()
                except Error as rollback_error:
                    print("The database connection was lost. Exiting the program.")
                    show_error_details(rollback_error)
                    break
                pause_for_menu()
            except ValueError as error:
                print("Invalid application input.")
                show_error_details(error)
                pause_for_menu()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")
    finally:
        if connection is not None:
            try:
                if connection.is_connected():
                    close_connection(connection)
            except Error as error:
                print("Could not close the database connection cleanly.")
                show_error_details(error)


if __name__ == "__main__":
    main()
