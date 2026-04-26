from flask import Flask, request, jsonify, render_template
from pydantic import ValidationError
from flask_cors import CORS

from postdetection import handle_predict, handle_extract, handle_extract_and_predict
from predetection import handle_predetection
from dtos import Article, HTMLPayload
from utils import display_dict
from config import Config

import os

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def root():
    return render_template("root.html")

@app.route("/extract", methods=["POST"])
def extract():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        if Config.RESTRICTED and not validate_access(request):
            return jsonify({"error": "Unauthorized"}), 403
        data = request.get_json()
        app.logger.info(f"Received request for /extract endpoint with payload {display_dict(data)}")
        html_payload = HTMLPayload(**data)
        article = handle_extract(html_payload)
        return jsonify(article.model_dump())
    except (ValidationError, Exception) as e:
        return jsonify({"error": str(e)}), 400

@app.route("/predict", methods=["POST"])
def predict():
    if request.method == 'OPTIONS':
        return '', 204  # Return 204 No Content for OPTIONS requests
    try:
        if Config.RESTRICTED and not validate_access(request):
            return jsonify({"error": "Unauthorized"}), 403
        data = request.get_json()
        app.logger.info(f"Received request for /predict endpoint with payload {display_dict(data)}")
        article = Article(**data)
        prediction = handle_predict(article)
        return jsonify(prediction.model_dump())
    except (ValidationError, Exception) as e:
        return jsonify({"error": str(e)}), 400

@app.route("/extract_and_predict", methods=["POST"])
def extract_and_predict():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        if Config.RESTRICTED and not validate_access(request):
            return jsonify({"error": "Unauthorized"}), 403
        
        data = request.get_json()
        app.logger.info(f"Received request for /extract_and_predict endpoint with payload {display_dict(data)}")
        html_payload = HTMLPayload(**data)
        generate_spoiler = data.get("generateSpoiler", True)
        prediction = handle_extract_and_predict(html_payload, generate_spoiler=generate_spoiler)

        return jsonify(prediction.model_dump())
    except (ValidationError, Exception) as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/predetect", methods=["POST"])
async def detect():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        if Config.RESTRICTED and not validate_access(request):
            return jsonify({"error": "Unauthorized"}), 403      
        data = request.get_json()
        app.logger.info(f"Received request for /predetect endpoint with payload {display_dict(data)}")
        html_payload = HTMLPayload(**data)
        prediction = await handle_predetection(html_payload)
        return jsonify(prediction.model_dump())
    except (ValidationError, Exception) as e:
        return jsonify({"error": str(e)}), 400


def validate_access(request):
    """ validates access based on the origin header and a special token """
    origin = request.headers.get("Origin", "")
    # if origin == f"chrome-extension://{Config.EXTENSION_ID}":
    if origin.startswith("chrome-extension://"):
        return True
    token = request.get_json().get("token")
    if token == Config.SPECIAL_TOKEN:
        return True
    return False


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
