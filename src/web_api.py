from flask import Flask, request, jsonify, abort
from CurrencyConverter import CurrencyConverter
from requests.exceptions import HTTPError, ConnectionError

app = Flask(__name__)


@app.route("/currency_converter", methods=["GET"])
def currency_converter():
    amount = request.args.get("amount")
    input_currency = request.args.get("input_currency")
    output_currency = request.args.get("output_currency")

    # amount and input_currency are required
    if amount is None or input_currency is None:
        abort(400)

    # amount has to be valid float
    try:
        amount = float(amount)
    except ValueError:
        abort(400)

    c = CurrencyConverter()

    # handle errors from conversion
    try:
        output = c.convert(amount, input_currency, output_currency)
    except (HTTPError, ConnectionError):
        abort(503)  # server error, API unavailable
    except KeyError:
        abort(400)  # client error, invalud currency code

    return jsonify(output)


if __name__ == "__main__":
    app.run()
