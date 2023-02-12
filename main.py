import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = "QYEM7AU9Qdax"
# you can get API keys for free here - https://api-docs.pgamerx.com/
RSA_API_KEY = "10230c3e63ff43d7b27101645231202"


app = Flask(__name__)


def generate_weather(city: str, date: str):
    url_base_url = "http://api.weatherapi.com/v1"
    url_api = "history.json"
    url_fin = "?"

    if city:
        url_fin += f"q={city}&"
    if date:
        url_fin += f"dt={date}"

    url = f"{url_base_url}/{url_api}{url_fin}"

    payload = {}
    headers = {"key": RSA_API_KEY}

    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas. Weather API</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def weather_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    if json_data.get("location") is None:
        raise InvalidUsage("location is required", status_code=400)

    city = json_data.get("location")

    if json_data.get("requester_name") is None:
        raise InvalidUsage("requester name is required", status_code=400)

    req_name = json_data.get("requester_name")

    if json_data.get("date") is None:
        raise InvalidUsage("date is required", status_code=400)

    date = json_data.get("date")

    weather = generate_weather(city, date)['forecast']['forecastday'][0]['day']

    ts = dt.datetime.now()

    result = {
        "requester_name": req_name,
        "timestamp": ts.isoformat(),
        "location": city,
        "date": date,
        "weather": weather,
    }

    return result