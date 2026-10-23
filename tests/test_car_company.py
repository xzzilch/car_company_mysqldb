"""Small tests for input validation and the summary report."""

import contextlib
from decimal import Decimal
import io
import unittest
from unittest.mock import patch

import car_company


class FakeCursor:
    """Return sample rows for the summary's three SELECT queries."""

    def __init__(self):
        self.rows = []

    def execute(self, query):
        if "SELECT car_id, model, price" in query:
            self.rows = [(1, "City LX", Decimal("1250000.00"))]
        elif "FROM production GROUP BY" in query:
            self.rows = [(1, 120)]
        elif "FROM sales GROUP BY" in query:
            self.rows = [(1, 35)]

    def fetchall(self):
        return self.rows

    def close(self):
        pass


class FakeConnection:
    def cursor(self):
        return FakeCursor()


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

    def test_id_must_appear_in_allowed_list(self):
        with patch("builtins.input", side_effect=["99", "1"]):
            self.assertEqual(car_company.read_existing_id("ID: ", [1]), 1)


class SummaryTests(unittest.TestCase):
    def test_summary_shows_grouped_production_and_sales(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            car_company.show_summary(FakeConnection())

        self.assertIn("City LX | Produced 120", output.getvalue())
        self.assertIn("Produced 120", output.getvalue())
        self.assertIn("Sold 35", output.getvalue())
        self.assertNotIn("\033", output.getvalue())

    def test_screen_clear_runs_only_for_interactive_terminal(self):
        output = FakeTerminal()
        input_terminal = FakeTerminal()
        with patch("car_company.sys.stdout", output):
            with patch("car_company.sys.stdin", input_terminal):
                car_company.clear_screen()

        self.assertEqual(output.getvalue(), "\033[2J\033[H")

    def test_screen_clear_is_skipped_when_output_is_redirected(self):
        output = io.StringIO()
        with patch("car_company.sys.stdout", output):
            with patch("car_company.sys.stdin", FakeTerminal()):
                car_company.clear_screen()

        self.assertEqual(output.getvalue(), "")

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
