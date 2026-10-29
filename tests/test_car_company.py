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

    def execute(self, query):
        if "SELECT car_id, model, price" in query:
            self.rows = [(1, "City LX", Decimal("1250000.00"))]
        elif "FROM production GROUP BY" in query:
            self.rows = self.produced
        elif "FROM sales GROUP BY" in query:
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


class InputValidationTests(unittest.TestCase):
    def test_integer_rejects_values_outside_mysql_int_range(self):
        with patch("builtins.input", side_effect=["2147483648", "7"]):
            self.assertEqual(car_company.read_positive_integer("Number: "), 7)

    def test_price_rejects_more_than_two_decimal_places(self):
        with patch("builtins.input", side_effect=["1.234", "1.23"]):
            self.assertEqual(car_company.read_price("Price: "), Decimal("1.23"))

    def test_date_requires_year_month_day_format(self):
        with patch("builtins.input", side_effect=["20261023", "2026-10-23"]):
            self.assertEqual(car_company.read_date("Date: "), "2026-10-23")

    def test_date_rejects_values_before_mysql_date_range(self):
        with patch("builtins.input", side_effect=["0999-12-31", "1000-01-01"]):
            self.assertEqual(car_company.read_date("Date: "), "1000-01-01")

    def test_id_must_appear_in_allowed_list(self):
        with patch("builtins.input", side_effect=["99", "1"]):
            self.assertEqual(car_company.read_existing_id("ID: ", [1]), 1)


class SummaryTests(unittest.TestCase):
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
