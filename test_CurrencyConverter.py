import unittest
from unittest.mock import patch
from src.CurrencyConverter import CurrencyConverter


class TestParseSymbol(unittest.TestCase):
    """Tests the parse_symbol method."""

    def setUp(self):
        self.converter = CurrencyConverter()

    def test_symbols(self):
        self.assertEqual(self.converter.parse_symbol("$"), "USD")
        self.assertEqual(self.converter.parse_symbol("€"), "EUR")
        self.assertEqual(self.converter.parse_symbol("Kč"), "CZK")
        self.assertEqual(self.converter.parse_symbol("£"), "GBP")
        self.assertEqual(self.converter.parse_symbol("¥"), "CNY")
        self.assertEqual(self.converter.parse_symbol("₽"), "RUB")

    def test_notSymbols(self):
        not_symbol = ["USD", "1x", ".23"]
        for ns in not_symbol:
            self.assertEqual(self.converter.parse_symbol(ns), ns)


class TestCalculateConversion(unittest.TestCase):
    """Tests the test_conversion method."""

    def setUp(self):
        self.converter = CurrencyConverter()
        # rates relative to EUR, actual on 11.1.2019
        self.USD_rate = 0.87  # 1USD = 0.86764 EUR
        self.EUR_rate = 1
        self.CZK_rate = 0.04

    def test_conversion_trivial(self):
        """Test trivial conversions to EUR."""
        self.assertAlmostEqual(
            self.converter.calculate_conversion(1, self.USD_rate, self.EUR_rate),
            self.USD_rate,
        )
        self.assertAlmostEqual(
            self.converter.calculate_conversion(1, self.CZK_rate, self.EUR_rate),
            self.CZK_rate,
        )

    def test_conversion_reverse(self):
        """Test reverse conversions."""
        amount = 1
        conversion = self.converter.calculate_conversion(
            amount, self.USD_rate, self.CZK_rate
        )
        reverse_conversion = self.converter.calculate_conversion(
            conversion, self.CZK_rate, self.USD_rate
        )
        self.assertAlmostEqual(reverse_conversion, amount)

        amount = 5.2
        conversion = self.converter.calculate_conversion(
            amount, self.EUR_rate, self.CZK_rate
        )
        reverse_conversion = self.converter.calculate_conversion(
            conversion, self.CZK_rate, self.EUR_rate
        )
        self.assertAlmostEqual(reverse_conversion, amount)

    def test_conversion_explicit(self):
        """Tests conversion with explicit values."""
        usd_to_eur = {3.21: 2.79, 6.12: 5.32, 5.18: 4.51, 658.33: 572.75, 0.12: 0.1}
        for amount, expected in usd_to_eur.items():
            self.assertAlmostEqual(
                self.converter.calculate_conversion(
                    amount, self.USD_rate, self.EUR_rate
                ),
                expected,
            )

        czk_to_usd = {3.21: 0.15, 6.12: 0.28, 5.18: 0.24, 658.33: 30.27, 0.12: 0.01}
        for amount, expected in czk_to_usd.items():
            self.assertAlmostEqual(
                self.converter.calculate_conversion(
                    amount, self.CZK_rate, self.USD_rate
                ),
                expected,
            )


class TestConvert(unittest.TestCase):
    """Tests the convert method."""

    def setUp(self):
        self.converter = CurrencyConverter()
        self.rates = {"USD": 0.87, "EUR": 1, "CZK": 0.04}

    @patch("src.CurrencyConverter.CurrencyConverter.get_conversion_rates")
    def test_single_conversion(self, mock_rates):
        """Test conversion 1:1."""
        mock_rates.return_value = self.rates

        conversion = self.converter.convert(1, "USD", "EUR")
        expected = {"input": {"amount": 1, "currency": "USD"}, "output": {"EUR": 0.87}}
        self.assertDictEqual(conversion, expected)

        conversion = self.converter.convert(1, "CZK", "USD")
        expected = {"input": {"amount": 1, "currency": "CZK"}, "output": {"USD": 0.05}}
        self.assertDictEqual(conversion, expected)

    @patch("src.CurrencyConverter.CurrencyConverter.get_conversion_rates")
    def test_all_conversion(self, mock_rates):
        """Test conversion 1:ALL."""
        mock_rates.return_value = self.rates

        conversion = self.converter.convert(1, "USD")
        expected = {
            "input": {"amount": 1, "currency": "USD"},
            "output": {"USD": 1, "EUR": 0.87, "CZK": 21.75},
        }
        self.assertDictEqual(conversion, expected)


if __name__ == "__main__":
    unittest.main()
