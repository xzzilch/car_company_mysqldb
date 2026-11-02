"""Small tests for input validation and the summary report."""

import contextlib
from decimal import Decimal
import io
import unittest
from unittest.mock import patch

import car_company


class FakeCursor:
    """Return configurable rows for the summary's three SELECT queries."""

    def __init__(self, produced=None, sold=None):
        self.rows = []
        self.produced = [(1, 120)] if produced is None else produced
        self.sold = [(1, 35)] if sold is None else sold

    def execute(self, query, parameters=None):
        if "SELECT car_id, model, price" in query:
            self.rows = [
                (
                    1,
                    "City LX",
                    Decimal("1250000.00"),
                    "Honda",
                    2026,
                    "Blue",
                    False,
                )
            ]
        elif "FROM production " in query and "GROUP BY" in query:
            self.rows = self.produced
        elif "FROM sales " in query and "GROUP BY" in query:
            self.rows = self.sold

    def fetchall(self):
        return self.rows

    def close(self):
        pass


class FakeConnection:
    def __init__(self, produced=None, sold=None):
        self.produced = produced
        self.sold = sold

    def cursor(self):
        return FakeCursor(self.produced, self.sold)


class FakeStartupConnection:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class FakeTerminal(io.StringIO):
    def isatty(self):
        return True


class FakeUpdateCursor:
    def __init__(self, rowcount, row_exists=False):
        self.rowcount = rowcount
        self.row_exists = row_exists
        self.query = None
        self.parameters = None

    def execute(self, query, parameters):
        self.query = query
        self.parameters = parameters

    def fetchone(self):
        return (1,) if self.row_exists else None


class FakeSchemaCursor:
    def __init__(self, schemas, race_on_alter=None):
        self.schemas = schemas
        self.race_on_alter = race_on_alter
        self.rows = []
        self.queries = []

    def execute(self, query):
        self.queries.append(query)
        if query.startswith("SHOW COLUMNS FROM"):
            table = query.split("`")[1]
            self.rows = [(name,) for name in self.schemas[table]]
        elif query.startswith("ALTER TABLE"):
            table, column = query.split("`")[1], query.split("`")[3]
            if self.race_on_alter == (table, column):
                self.schemas[table].add(column)
                self.race_on_alter = None
                raise car_company.Error(
                    f"Duplicate column name '{column}'", errno=1060
                )
            self.schemas[table].add(column)

    def fetchall(self):
        return self.rows

    def close(self):
        pass


class FakeSchemaConnection:
    def __init__(self, race_on_alter=None):
        self.schemas = {
            "cars": {"car_id", "model", "price"},
            "production": {
                "production_id",
                "car_id",
                "production_date",
                "quantity",
            },
            "sales": {"sale_id", "car_id", "sale_date", "quantity"},
        }
        self.query_cursor = FakeSchemaCursor(self.schemas, race_on_alter)
        self.committed = False

    def cursor(self):
        return self.query_cursor

    def commit(self):
        self.committed = True


class FakeWriteCursor:
    def __init__(self, error=None):
        self.error = error
        self.query = None
        self.parameters = None
        self.closed = False
        self.rowcount = 1

    def execute(self, query, parameters):
        self.query = query
        self.parameters = parameters
        if self.error:
            raise self.error

    def close(self):
        self.closed = True


class FakeWriteConnection:
    def __init__(self, error=None, commit_error=None, rollback_error=None):
        self.query_cursor = FakeWriteCursor(error)
        self.commit_error = commit_error
        self.rollback_error = rollback_error
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return self.query_cursor

    def commit(self):
        if self.commit_error:
            raise self.commit_error
        self.committed = True

    def rollback(self):
        self.rolled_back = True
        if self.rollback_error:
            raise self.rollback_error


class FakeResultCursor:
    def __init__(self, rows):
        self.rows = rows
        self.query = None
        self.closed = False

    def execute(self, query):
        self.query = query

    def fetchall(self):
        return self.rows

    def close(self):
        self.closed = True


class FakeResultConnection:
    def __init__(self, rows):
        self.query_cursor = FakeResultCursor(rows)

    def cursor(self):
        return self.query_cursor

    def commit(self):
        pass


class FakeTotalsCursor:
    def __init__(self, rows):
        self.rows = rows
        self.query = None
        self.parameters = None

    def execute(self, query, parameters):
        self.query = query
        self.parameters = parameters

    def fetchall(self):
        return self.rows

    def close(self):
        pass


class FakeTotalsConnection:
    def __init__(self, rows):
        self.query_cursor = FakeTotalsCursor(rows)

    def cursor(self):
        return self.query_cursor


class InputValidationTests(unittest.TestCase):
    def test_integer_rejects_values_outside_mysql_int_range(self):
        with patch("builtins.input", side_effect=["2147483648", "7"]):
            self.assertEqual(car_company.read_positive_integer("Number: "), 7)

    def test_price_rejects_more_than_two_decimal_places(self):
        with patch("builtins.input", side_effect=["1.234", "1.23"]):
            self.assertEqual(car_company.read_price("Price: "), Decimal("1.23"))

    def test_price_rejects_scientific_notation_and_extremely_long_values(self):
        with patch(
            "builtins.input",
            side_effect=["1e2", "9" * 10000, ".5"],
        ):
            self.assertEqual(car_company.read_price("Price: "), Decimal("0.5"))

    def test_price_accepts_leading_zeroes_when_value_is_in_range(self):
        with patch("builtins.input", return_value="0000000001.25"):
            self.assertEqual(car_company.read_price("Price: "), Decimal("1.25"))

    def test_date_requires_year_month_day_format(self):
        with patch("builtins.input", side_effect=["20261023", "2026-10-23"]):
            self.assertEqual(car_company.read_date("Date: "), "2026-10-23")

    def test_date_rejects_values_before_mysql_date_range(self):
        with patch("builtins.input", side_effect=["0999-12-31", "1000-01-01"]):
            self.assertEqual(car_company.read_date("Date: "), "1000-01-01")

    def test_date_accepts_leap_day_and_mysql_upper_boundary(self):
        with patch("builtins.input", return_value="2024-02-29"):
            self.assertEqual(car_company.read_date("Date: "), "2024-02-29")
        with patch("builtins.input", return_value="9999-12-31"):
            self.assertEqual(car_company.read_date("Date: "), "9999-12-31")

    def test_date_rejects_invalid_leap_day_and_non_iso_formats(self):
        with patch(
            "builtins.input",
            side_effect=["2023-02-29", "20261023", "2026-10-23"],
        ):
            self.assertEqual(car_company.read_date("Date: "), "2026-10-23")

    def test_empty_default_date_uses_today_and_future_dates_are_allowed(self):
        with patch.object(car_company, "date") as date_type:
            date_type.today.return_value.isoformat.return_value = "2026-11-02"
            with patch("builtins.input", return_value=""):
                self.assertEqual(
                    car_company.read_date("Date: ", default_today=True),
                    "2026-11-02",
                )
        with patch("builtins.input", return_value="9999-12-31"):
            self.assertEqual(car_company.read_date("Date: "), "9999-12-31")

    def test_text_validation_rejects_control_characters(self):
        with patch("builtins.input", side_effect=["line\nbreak", "Matte Blue"]):
            self.assertEqual(
                car_company.read_text("Color: ", "a color", 30), "Matte Blue"
            )

    def test_menu_prompt_has_separator_and_consistent_prompt_marker(self):
        output = io.StringIO()
        with patch("builtins.input", return_value="4") as prompt:
            with contextlib.redirect_stdout(output):
                result = car_company.read_input("Choose an option: ", separator=True)

        self.assertEqual(result, "4")
        self.assertIn("_" * 12, output.getvalue())
        prompt.assert_called_once_with("  > Choose an option: ")

    def test_id_must_appear_in_allowed_list(self):
        with patch("builtins.input", side_effect=["99", "1"]):
            self.assertEqual(car_company.read_existing_id("ID: ", [1]), 1)

    def test_integer_rejects_extremely_long_values_without_crashing(self):
        with patch("builtins.input", side_effect=["9" * 10000, "4"]):
            self.assertEqual(car_company.read_positive_integer("Number: "), 4)

    def test_small_integer_and_boolean_inputs_are_validated(self):
        with patch("builtins.input", side_effect=["65536", "1885", "2026"]):
            self.assertEqual(
                car_company.read_integer_range("Year: ", 1886, 65535), 2026
            )
        with patch("builtins.input", side_effect=["maybe", "yes"]):
            self.assertTrue(car_company.read_yes_no("Electric: "))

    def test_car_model_year_allows_two_years_ahead_but_not_unbounded_years(self):
        prompts = []
        inputs = iter(
            ["City LX", "1000", "Honda", "2029", "2028", "Blue", "n"]
        )

        def fake_input(prompt):
            prompts.append(prompt)
            return next(inputs)

        with patch.object(car_company, "date") as date_type:
            date_type.today.return_value.year = 2026
            with patch("builtins.input", side_effect=fake_input):
                details = car_company.read_car_details()

        self.assertEqual(details[3], 2028)
        self.assertIn("model year (1886-2028)", prompts[3])

    def test_production_and_sales_details_match_schema(self):
        with patch("builtins.input", side_effect=["", "Night", "n"]):
            self.assertEqual(
                car_company.read_record_details("production"), ("Night", False)
            )
        with patch("builtins.input", side_effect=["Online", "Card", "24"]):
            self.assertEqual(
                car_company.read_record_details("sales"), ("Online", "Card", 24)
            )

    def test_unsupported_record_table_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported record table"):
            car_company.get_record_config("unknown")


class SchemaMigrationTests(unittest.TestCase):
    def test_duplicate_column_from_concurrent_migration_is_treated_as_complete(self):
        connection = FakeSchemaConnection(race_on_alter=("cars", "manufacturer"))

        car_company.create_tables(connection)

        self.assertTrue(
            set(car_company.CAR_COLUMNS).issubset(connection.schemas["cars"])
        )
        self.assertTrue(connection.committed)

    def test_new_columns_are_added_to_existing_tables_without_dropping_data(self):
        connection = FakeSchemaConnection()

        car_company.create_tables(connection)

        self.assertEqual(
            connection.schemas["cars"],
            {"car_id", "model", "price", *car_company.CAR_COLUMNS},
        )
        self.assertEqual(
            connection.schemas["production"],
            {
                "production_id",
                "car_id",
                "production_date",
                "quantity",
                *car_company.RECORD_COLUMNS["production"],
            },
        )
        self.assertEqual(
            connection.schemas["sales"],
            {
                "sale_id",
                "car_id",
                "sale_date",
                "quantity",
                *car_company.RECORD_COLUMNS["sales"],
            },
        )
        self.assertTrue(connection.committed)
        self.assertFalse(any("DROP" in query for query in connection.query_cursor.queries))


class CarOperationTests(unittest.TestCase):
    def test_show_cars_includes_the_new_car_fields(self):
        rows = [
            (1, "City LX", Decimal("1250000.00"), "Honda", 2026, "Blue", True)
        ]
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            displayed = car_company.show_cars(FakeResultConnection(rows))

        self.assertEqual(displayed, rows)
        self.assertIn("Honda", output.getvalue())
        self.assertIn("2026", output.getvalue())
        self.assertIn("Blue", output.getvalue())
        self.assertIn("Yes", output.getvalue())

    def test_add_car_inserts_all_validated_fields(self):
        connection = FakeWriteConnection()
        details = (
            "City LX",
            Decimal("1250000.00"),
            "Honda",
            2026,
            "Blue",
            True,
        )

        with patch("car_company.read_car_details", return_value=details):
            with contextlib.redirect_stdout(io.StringIO()):
                car_company.add_car(connection)

        self.assertIn("manufacturer, model_year, color, is_electric", connection.query_cursor.query)
        self.assertEqual(connection.query_cursor.parameters, details)
        self.assertTrue(connection.committed)
        self.assertFalse(connection.rolled_back)
        self.assertTrue(connection.query_cursor.closed)

    def test_add_production_record_saves_new_fields(self):
        connection = FakeWriteConnection()

        with patch("car_company.show_cars", return_value=[(1,)]):
            with patch("car_company.read_existing_id", return_value=1):
                with patch(
                    "car_company.read_date", return_value="2026-11-02"
                ) as read_date:
                    with patch("car_company.read_positive_integer", return_value=8):
                        with patch(
                            "car_company.read_record_details",
                            return_value=("Night", True),
                        ):
                            with contextlib.redirect_stdout(io.StringIO()):
                                car_company.add_record(connection, "production")

        read_date.assert_called_once_with(
            "Production date (YYYY-MM-DD, future dates allowed) [today]: ",
            default_today=True,
        )
        self.assertIn("shift, quality_checked", connection.query_cursor.query)
        self.assertEqual(
            connection.query_cursor.parameters,
            (1, "2026-11-02", 8, "Night", True),
        )
        self.assertTrue(connection.committed)

    def test_update_sales_record_saves_all_new_fields(self):
        connection = FakeWriteConnection()

        with patch(
            "car_company.show_records",
            return_value=[(3, 1, "City LX", "2026-01-01", 2)],
        ):
            with patch("car_company.show_cars", return_value=[(1,)]):
                with patch(
                    "car_company.read_existing_id", side_effect=[3, 1]
                ):
                    with patch(
                        "car_company.read_date", return_value="2026-11-02"
                    ) as read_date:
                        with patch(
                            "car_company.read_positive_integer", return_value=5
                        ):
                            with patch(
                                "car_company.read_record_details",
                                return_value=("Online", "Card", 24),
                            ):
                                with contextlib.redirect_stdout(io.StringIO()):
                                    car_company.update_record(connection, "sales")

        read_date.assert_called_once_with(
            "New sale date (YYYY-MM-DD, future dates allowed): "
        )
        self.assertIn(
            "sales_channel = %s, payment_method = %s, warranty_months = %s",
            connection.query_cursor.query,
        )
        self.assertEqual(
            connection.query_cursor.parameters,
            (1, "2026-11-02", 5, "Online", "Card", 24, 3),
        )
        self.assertTrue(connection.committed)

    def test_show_production_records_displays_new_fields(self):
        rows = [(4, 1, "City LX", "2026-11-02", 8, "Night", True)]
        connection = FakeResultConnection(rows)
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            car_company.show_records(connection, "production")

        self.assertIn("Night", output.getvalue())
        self.assertIn("Yes", output.getvalue())
        self.assertIn("r.shift, r.quality_checked", connection.query_cursor.query)
        self.assertTrue(connection.query_cursor.closed)

    def test_add_car_reports_query_and_rollback_errors(self):
        connection = FakeWriteConnection(error=car_company.Error("write failed"))
        output = io.StringIO()

        with patch(
            "car_company.read_car_details",
            return_value=("City LX", Decimal("1.00"), "Honda", 2026, "Blue", False),
        ):
            with contextlib.redirect_stdout(output):
                car_company.add_car(connection)

        self.assertIn("Could not add car", output.getvalue())
        self.assertIn("write failed", output.getvalue())
        self.assertTrue(connection.rolled_back)
        self.assertTrue(connection.query_cursor.closed)

    def test_commit_failure_rolls_back_and_reports_failure(self):
        connection = FakeWriteConnection(
            commit_error=car_company.Error("commit failed")
        )
        output = io.StringIO()

        with patch(
            "car_company.read_car_details",
            return_value=("City LX", Decimal("1.00"), "Honda", 2026, "Blue", False),
        ):
            with contextlib.redirect_stdout(output):
                car_company.add_car(connection)

        self.assertIn("commit failed", output.getvalue())
        self.assertTrue(connection.rolled_back)
        self.assertFalse(connection.committed)
        self.assertTrue(connection.query_cursor.closed)

    def test_rollback_failure_is_reported_and_propagated(self):
        connection = FakeWriteConnection(
            error=car_company.Error("write failed"),
            rollback_error=car_company.Error("rollback failed"),
        )
        output = io.StringIO()

        with patch(
            "car_company.read_car_details",
            return_value=("City LX", Decimal("1.00"), "Honda", 2026, "Blue", False),
        ):
            with contextlib.redirect_stdout(output):
                with self.assertRaisesRegex(car_company.Error, "rollback failed"):
                    car_company.add_car(connection)

        self.assertIn("write failed", output.getvalue())
        self.assertIn("rollback failed", output.getvalue())
        self.assertTrue(connection.query_cursor.closed)


class DeleteConfirmationTests(unittest.TestCase):
    def test_invalid_answer_repeats_until_delete_is_declined(self):
        with patch("builtins.input", side_effect=["maybe", "n"]):
            self.assertFalse(car_company.confirm_delete())

    def test_invalid_answer_repeats_until_delete_is_confirmed(self):
        with patch("builtins.input", side_effect=["maybe", "Y"]):
            self.assertTrue(car_company.confirm_delete())


class UpdateResultTests(unittest.TestCase):
    def run_update_result(self, cursor):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            car_company.report_update_result(
                cursor,
                "cars",
                "car_id",
                7,
                "Car updated.",
                "No changes needed.",
                "No car found with that ID.",
            )
        return output.getvalue()

    def test_changed_row_reports_success_without_extra_query(self):
        cursor = FakeUpdateCursor(rowcount=1)

        self.assertIn("Car updated.", self.run_update_result(cursor))
        self.assertIsNone(cursor.query)

    def test_unchanged_existing_row_is_not_reported_missing(self):
        cursor = FakeUpdateCursor(rowcount=0, row_exists=True)

        self.assertIn("No changes needed.", self.run_update_result(cursor))
        self.assertEqual(cursor.query, "SELECT 1 FROM cars WHERE car_id = %s")
        self.assertEqual(cursor.parameters, (7,))

    def test_missing_row_reports_missing(self):
        cursor = FakeUpdateCursor(rowcount=0, row_exists=False)

        self.assertIn("No car found with that ID.", self.run_update_result(cursor))


class SummaryTests(unittest.TestCase):
    def test_totals_filter_future_records_using_bound_as_of_date(self):
        as_of = car_company.date(2026, 11, 2)

        for table, date_column in (
            ("production", "production_date"),
            ("sales", "sale_date"),
        ):
            connection = FakeTotalsConnection([(1, 120)])
            totals = car_company.get_totals(connection, table, as_of)

            self.assertEqual(totals, {1: 120})
            self.assertIn(
                f"WHERE {date_column} <= %s", connection.query_cursor.query
            )
            self.assertEqual(connection.query_cursor.parameters, (as_of,))

    def test_summary_uses_one_cutoff_date_for_both_totals(self):
        car = (1, "City LX", Decimal("1.00"), "Honda", 2026, "Blue", False)
        calls = []

        def fake_totals(connection, table, as_of):
            calls.append((table, as_of))
            return {}

        output = io.StringIO()
        with patch.object(car_company, "date") as date_type:
            date_type.today.return_value.isoformat.return_value = "2026-11-02"
            with patch("car_company.fetch_cars", return_value=[car]):
                with patch("car_company.get_totals", side_effect=fake_totals):
                    with contextlib.redirect_stdout(output):
                        car_company.show_summary(FakeConnection())

        self.assertEqual(
            calls,
            [
                ("production", date_type.today.return_value),
                ("sales", date_type.today.return_value),
            ],
        )
        self.assertIn("Totals through 2026-11-02", output.getvalue())

    def test_table_escapes_control_characters_and_handles_wide_text(self):
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            car_company.print_table(
                ("Model", "Color"),
                [("City\n\x1b[31m", "東京")],
                max_widths=(12, 4),
            )

        self.assertIn(r"\n", output.getvalue())
        self.assertNotIn("\x1b", output.getvalue())
        self.assertTrue(all(len(line) <= 23 for line in output.getvalue().splitlines()))

    def test_error_details_escape_terminal_control_sequences(self):
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            car_company.show_error_details(Exception("bad\x1b[31m error\ncontinued"))

        self.assertNotIn("\x1b", output.getvalue())
        self.assertIn(r"\x1b[31m", output.getvalue())
        self.assertIn(r"\n", output.getvalue())

    def test_table_rejects_mismatched_rows_or_layout(self):
        with self.assertRaisesRegex(ValueError, "same number of cells"):
            car_company.print_table(("ID", "Model"), [(1,)])
        with self.assertRaisesRegex(ValueError, "one entry per"):
            car_company.print_table(("ID", "Model"), [], max_widths=(4,))
        with self.assertRaisesRegex(ValueError, "positive integers"):
            car_company.print_table(("ID",), [], max_widths=(1.5,))

    def test_summary_shows_grouped_production_and_sales(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            car_company.show_summary(FakeConnection())

        self.assertIn("Car model", output.getvalue())
        self.assertIn("Produced | Sold | Cars left", output.getvalue())
        self.assertIn("City LX", output.getvalue())
        self.assertIn("|      120 |   35 |        85", output.getvalue())
        self.assertNotIn("\033", output.getvalue())

    def test_summary_shows_zero_when_no_records_exist(self):
        output = io.StringIO()
        connection = FakeConnection(produced=[], sold=[])

        with contextlib.redirect_stdout(output):
            car_company.show_summary(connection)

        self.assertIn("|        0 |    0 |         0", output.getvalue())

    def test_summary_handles_either_missing_total(self):
        production_only = io.StringIO()
        with contextlib.redirect_stdout(production_only):
            car_company.show_summary(
                FakeConnection(produced=[(1, 120)], sold=[])
            )

        sales_only = io.StringIO()
        with contextlib.redirect_stdout(sales_only):
            car_company.show_summary(
                FakeConnection(produced=[], sold=[(1, 35)])
            )

        self.assertIn("|      120 |    0 |       120", production_only.getvalue())
        self.assertIn("|        0 |   35 |       -35", sales_only.getvalue())

    def test_summary_shows_negative_stock_when_sales_exceed_production(self):
        output = io.StringIO()
        connection = FakeConnection(produced=[(1, 10)], sold=[(1, 12)])

        with contextlib.redirect_stdout(output):
            car_company.show_summary(connection)

        self.assertIn("|       10 |   12 |        -2", output.getvalue())

    def test_summary_truncates_long_model_names_without_shifting_columns(self):
        connection = FakeConnection()
        output = io.StringIO()
        long_car = (1, "A very long car model name that will overflow", Decimal("1.00"))
        with patch("car_company.fetch_cars", return_value=[long_car]):
            with contextlib.redirect_stdout(output):
                car_company.show_summary(connection)

        self.assertIn("A very long car model name ... |", output.getvalue())
        self.assertIn("|      120 |   35 |        85", output.getvalue())

    def test_summary_expands_numeric_columns_for_large_totals(self):
        connection = FakeConnection(
            produced=[(1, 12345678901)],
            sold=[(1, 1234567890)],
        )
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            car_company.show_summary(connection)

        self.assertIn("| 12345678901 | 1234567890 | 11111111011", output.getvalue())

    def test_table_truncates_long_cells_and_fits_narrow_terminal(self):
        output = io.StringIO()
        with patch("car_company.shutil.get_terminal_size") as get_terminal_size:
            get_terminal_size.return_value.columns = 44
            with contextlib.redirect_stdout(output):
                car_company.print_table(
                    ("ID", "Model", "Manufacturer"),
                    [(12345, "A very long model name", "A very long manufacturer")],
                    max_widths=(8, 24, 24),
                )

        lines = output.getvalue().splitlines()
        self.assertTrue(all(len(line) <= 40 for line in lines))
        self.assertIn("...", output.getvalue())

    def test_screen_clear_uses_windows_command_for_interactive_terminal(self):
        output = FakeTerminal()
        input_terminal = FakeTerminal()
        with patch("car_company.sys.stdout", output):
            with patch("car_company.sys.stdin", input_terminal):
                with patch("car_company.os.name", "nt"):
                    with patch("car_company.os.system") as system:
                        car_company.clear_screen()

        system.assert_called_once_with("cls")

    def test_screen_clear_uses_unix_command_for_interactive_terminal(self):
        with patch("car_company.sys.stdout", FakeTerminal()):
            with patch("car_company.sys.stdin", FakeTerminal()):
                with patch("car_company.os.name", "posix"):
                    with patch("car_company.os.system") as system:
                        car_company.clear_screen()

        system.assert_called_once_with("clear")

    def test_screen_clear_is_skipped_when_output_is_redirected(self):
        output = io.StringIO()
        with patch("car_company.sys.stdout", output):
            with patch("car_company.sys.stdin", FakeTerminal()):
                with patch("car_company.os.system") as system:
                    car_company.clear_screen()

        self.assertEqual(output.getvalue(), "")
        system.assert_not_called()

    def test_heading_does_not_clear_context(self):
        output = io.StringIO()
        with patch.object(car_company, "clear_screen") as clear_screen:
            with contextlib.redirect_stdout(output):
                car_company.print_heading("CARS")

        clear_screen.assert_not_called()
        self.assertIn("CARS", output.getvalue())


class StartupCleanupTests(unittest.TestCase):
    def test_connection_closes_when_startup_is_interrupted(self):
        connection = FakeStartupConnection()
        output = io.StringIO()

        with patch.object(car_company, "connect_to_database", return_value=connection):
            with patch.object(car_company, "create_tables", side_effect=KeyboardInterrupt):
                with contextlib.redirect_stdout(output):
                    car_company.main()

        self.assertTrue(connection.closed)


if __name__ == "__main__":
    unittest.main()
