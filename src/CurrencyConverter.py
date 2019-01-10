import requests
from redis import StrictRedis, ConnectionError, ResponseError, TimeoutError
import json


class CurrencyConverter:
    """
    Handles calling API, caching and converting currency.

        :param redis_config: connection details to Redis server (host, password, port) (opt.)
    """

    def __init__(self, redis_config=None):
        self.redis_key = "CurrencyConverter:rates"

        if redis_config is None:
            self.redis = None
            return

        try:
            self.redis = StrictRedis(socket_connect_timeout=3, **redis_config)
            self.redis.ping()  # if connection failed, ping throws exception
        except (ConnectionError, ResponseError, TimeoutError):
            self.redis = None

    def call_rates_api(self):
        """
        Calls api and return result as a dictionary.

            :raises HTTPError: API is unavailable
        """
        request = requests.get("https://api.skypicker.com/rates")

        request.raise_for_status()  # throw HTTPError if API is unavailable

        return request.json()

    def get_conversion_rates(self):
        """Returns dictionary of all available conversion rates."""
        if self.redis is None:
            return self.call_rates_api()

        rates = self.redis.get(self.redis_key)

        # nothing on redis, fetch from api and save it
        if rates is None:
            rates = self.call_rates_api()
            self.redis.setex(self.redis_key, 60 * 60, json.dumps(rates))
        else:
            rates = json.loads(rates)

        return rates

    def parse_symbol(self, symbol):
        """
        Converts currency symbol to code.

            :param symbol str: Currency code or symbol.
            :returns str: Currency code.
        """
        symbols = {
            "€": "EUR",
            "$": "USD",
            "Kč": "CZK",
            "£": "GBP",
            "¥": "CNY",
            "₽": "RUB",
        }  # I haven't found list of all symbol and code pairs in reasonable format, so I just listed the most important ones

        return symbols.get(
            symbol, symbol
        )  # return corresponding code, or the symbol itself if it doesnt exist

    def calculate_conversion(self, amount, source_rate, dest_rate):
        """
        Calculates conversion from one currency to another.
        
            :param amount float: amount to convert
            :param source_rate float: conversion rate for input_currency
            :param dest_rate float: conversion rate for output_currency
            :return float: amount converted to output_currency, rounded to 2 decimal points
        """
        return round(amount * source_rate / dest_rate, 2)

    def convert(self, amount, input_currency, output_currency=None):
        """
        Converts specified amount of source currency into another currency.

            :param amount float: amount to convert
            :param input_currency str: inputc currency code or symbol
            :param output_currency str: output currency code or symbol, if not specified, convert to all available currencies
            :return dict: dictionary with input parameters and output currencies
        """
        conversion_rates = self.get_conversion_rates()

        output_data = {}

        input_currency = self.parse_symbol(input_currency)

        if output_currency is None:
            # calculate all possible conversions
            for currency, rate in conversion_rates.items():
                output_data[currency] = self.calculate_conversion(
                    amount, conversion_rates[input_currency], rate
                )
        else:
            # calculate only specified destination currency
            output_currency = self.parse_symbol(output_currency)
            output_data[output_currency] = self.calculate_conversion(
                amount,
                conversion_rates[input_currency],
                conversion_rates[output_currency],
            )

        return {
            "input": {"amount": amount, "currency": input_currency},
            "output": output_data,
        }

