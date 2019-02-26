# CurrencyConvert
Simple currency converter with CLI and Web API.

CLI parameters:
* --amount *{float}*    
* --input_currency *{code or symbol}*
* --output_currency *{code or symbol}*  (optional parameter)

Web API:
    **GET /currency_converter**?amount=*{float}*&input_currency=*{code or symbol}*&output_currency=*{code or symbol}*

CurrencyConverter is a class which handles all external API calls (Skypicker) and currency conversions. It can use Redis for caching as well - just pass configuration to a constructor (optional).
Configuration should be a dictionary with "host", "port" and "password" keys and corresponding values.

There is test_CurrencyConverter.py file as well, which contains simple tests to test all functionality in CurrencyConverter class, except for Redis and API call.
