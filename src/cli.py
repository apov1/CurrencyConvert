from argparse import ArgumentParser
from CurrencyConverter import CurrencyConverter
from requests.exceptions import HTTPError, ConnectionError
import json

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--amount", help="Enter amount to convert", type=float, required=True
    )
    parser.add_argument(
        "--input_currency",
        help="Enter 3-letter code or symbol of currency, which you want to convert from",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--output_currency",
        help="Enter 3-letter code or symbol of currency, which you want to convert to (if not specified, converts to all available currencies)",
        type=str,
    )
    args = parser.parse_args()

    c = CurrencyConverter()

    try:
        output_json = json.dumps(
            c.convert(args.amount, args.input_currency, args.output_currency)
        )
    except (HTTPError, ConnectionError):
        output_json = json.dumps(
            {"error": "Currency API is not available at this time."}
        )
    except KeyError as err:
        output_json = json.dumps({"error": f"{err} is not a valid currency code."})

    print(output_json)
