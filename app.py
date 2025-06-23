from flask import Flask, request, jsonify, abort
import requests
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

AIRTABLE_BASE_ID = "appQfjuuBSHjxcuho"
TABLE_NAME = "Venues"
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_API_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}"

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json"
}

# Set your API token here
API_TOKEN = "patNqHDGqVoCNVqYa"

def check_auth():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        abort(401, description="Authentication required")
    token = auth_header.split(" ")[1]
    if token != API_TOKEN:
        abort(403, description="Invalid token")

@app.route('/venues', methods=['GET'])
def get_all_venues():
    check_auth()
    response = requests.get(AIRTABLE_API_URL, headers=HEADERS)
    return jsonify(response.json()), response.status_code

@app.route('/venues/search', methods=['GET'])
def search_venues():
    check_auth()
    name = request.args.get('name')
    min_capacity = request.args.get('min_capacity')
    bottle_service = request.args.get('bottle_service')

    formula_parts = []

    if name:
        formula_parts.append(f"FIND('{name}', {{Venue Name}}) > 0")
    if min_capacity:
        formula_parts.append(f"{{Capacity}} >= {min_capacity}")
    if bottle_service and bottle_service.strip().lower() in ["yes", "true", "1"]:
        formula_parts.append("{{Bottle Service Available?}} = 'Yes'")

    formula = "AND(" + ",".join(formula_parts) + ")" if formula_parts else ""

    params = {"filterByFormula": formula} if formula else {}

    response = requests.get(AIRTABLE_API_URL, headers=HEADERS, params=params)
    return jsonify(response.json()), response.status_code

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "API is running"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
