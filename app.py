from flask import Flask, request, jsonify, abort
import requests
from flask_cors import CORS
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

AIRTABLE_BASE_ID = "appQfjuuBSHjxcuho"
TABLE_NAME = "Venues"
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
print(f"DEBUG: AIRTABLE_TOKEN loaded from environment: {AIRTABLE_TOKEN}")
AIRTABLE_API_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}"

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json"
}

# Set your API token here
API_TOKEN = os.getenv("API_TOKEN")
print(f"DEBUG: API_TOKEN loaded from environment: {API_TOKEN}")

def check_auth():
    print("DEBUG: check_auth called")
    print(f"DEBUG: All request headers: {dict(request.headers)}")
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        # Try lowercase as fallback
        auth_header = request.headers.get("authorization")
        print(f"DEBUG: Fallback lowercase 'authorization': {auth_header}")
    if not auth_header:
        # Try custom header as fallback
        auth_header = request.headers.get("X-API-Key")
        print(f"DEBUG: Fallback 'X-API-Key': {auth_header}")
        if auth_header:
            token = auth_header
            print(f"DEBUG: Received token from X-API-Key: '{token}'")
            print(f"DEBUG: Expected token: '{API_TOKEN}'")
            if token != API_TOKEN:
                print("DEBUG: aborting with 403 - token does not match API_TOKEN")
                abort(403, description="Invalid token")
            return
    print(f"DEBUG: auth_header value: '{auth_header}' (length: {len(auth_header) if auth_header else 'None'})")
    print(f"DEBUG: auth_header.startswith('Bearer '): {auth_header.startswith('Bearer ') if auth_header else 'None'}")
    if not auth_header:
        print("DEBUG: aborting with 401 - auth_header is None or empty")
        abort(401, description="Authentication required")
    if not auth_header.startswith("Bearer "):
        print("DEBUG: aborting with 401 - auth_header does not start with 'Bearer '")
        abort(401, description="Authentication required")
    token = auth_header.split(" ")[1]
    print(f"DEBUG: Received token: '{token}' (length: {len(token)})")
    print(f"DEBUG: Expected token: '{API_TOKEN}' (length: {len(API_TOKEN)})")
    print(f"DEBUG: Tokens match? {token == API_TOKEN}")
    print(f"DEBUG: Token types - received: {type(token)}, expected: {type(API_TOKEN)}")
    if token != API_TOKEN:
        print("DEBUG: aborting with 403 - token does not match API_TOKEN")
        abort(403, description="Invalid token")

@app.route('/venues', methods=['GET'])
def get_all_venues():
    check_auth()
    print("DEBUG: Passed check_auth, about to call Airtable")
    response = requests.get(AIRTABLE_API_URL, headers=HEADERS)
    print(f"DEBUG: Airtable response status: {response.status_code}")
    print(f"DEBUG: Airtable response body: {response.text}")
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
    app.run(host='0.0.0.0', port=5002)
# trigger redeploy
# trigger redeploy
# trigger redeploy
