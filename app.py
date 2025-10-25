from flask import Flask, request, jsonify, make_response
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Developer tag
COPYRIGHT_STRING = "@mynk_mynk_mynk this source maker"

# Desired key order for output
DESIRED_ORDER = [
    "Owner Name", "Father's Name", "Owner Serial No", "Model Name", "Maker Model",
    "Vehicle Class", "Fuel Type", "Fuel Norms", "Registration Date", "Insurance Company",
    "Insurance No", "Insurance Expiry", "Insurance Upto", "Fitness Upto", "Tax Upto",
    "PUC No", "PUC Upto", "Financier Name", "Registered RTO", "Address", "City Name", "Phone"
]

# Environment variable for API key
MYNKAPI = os.environ.get("MYNKAPI", None)

# ---------------------------
# VEHICLE DETAILS SCRAPER
# ---------------------------
def get_vehicle_details(rc_number: str) -> dict:
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"

    headers = {
        "Host": "vahanx.in",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://vahanx.in/rc-search",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}
    except Exception as e:
        return {"error": str(e)}

    def get_value(label):
        try:
            div = soup.find("span", string=label).find_parent("div")
            return div.find("p").get_text(strip=True)
        except AttributeError:
            return None

    data = {
        "Owner Name": get_value("Owner Name"),
        "Father's Name": get_value("Father's Name"),
        "Owner Serial No": get_value("Owner Serial No"),
        "Model Name": get_value("Model Name"),
        "Maker Model": get_value("Maker Model"),
        "Vehicle Class": get_value("Vehicle Class"),
        "Fuel Type": get_value("Fuel Type"),
        "Fuel Norms": get_value("Fuel Norms"),
        "Registration Date": get_value("Registration Date"),
        "Insurance Company": get_value("Insurance Company"),
        "Insurance No": get_value("Insurance No"),
        "Insurance Expiry": get_value("Insurance Expiry"),
        "Insurance Upto": get_value("Insurance Upto"),
        "Fitness Upto": get_value("Fitness Upto"),
        "Tax Upto": get_value("Tax Upto"),
        "PUC No": get_value("PUC No"),
        "PUC Upto": get_value("PUC Upto"),
        "Financier Name": get_value("Financier Name"),
        "Registered RTO": get_value("Registered RTO"),
        "Address": get_value("Address"),
        "City Name": get_value("City Name"),
        "Phone": get_value("Phone")
    }
    return data


# ---------------------------
# ROUTES
# ---------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "🚗 Vehicle Info API by Mohd Kaif is running!",
        "developer": COPYRIGHT_STRING,
        "tag": "api by mynk"
    })


@app.route("/lookup", methods=["GET"])
def lookup_vehicle():
    # API Key validation
    if MYNKAPI:
        provided_key = request.headers.get("x-api-key") or request.args.get("key")
        if not provided_key or provided_key != MYNKAPI:
            return jsonify({"error": "Invalid or missing API key"}), 401

    rc_number = request.args.get("rc")
    if not rc_number:
        return jsonify({
            "error": "Please provide ?rc= parameter",
            "copyright": COPYRIGHT_STRING,
            "tag": "api by mynk"
        }), 400

    details = get_vehicle_details(rc_number)

    ordered_details = OrderedDict()
    for key in DESIRED_ORDER:
        if key in details:
            ordered_details[key] = details[key]

    ordered_details["copyright"] = COPYRIGHT_STRING
    ordered_details["tag"] = "api by mynk"

    # Add response header
    resp = make_response(jsonify(ordered_details))
    resp.headers["X-API-BY"] = "mynk"
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
