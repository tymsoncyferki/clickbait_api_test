from flask import Flask, request, jsonify, render_template
from pydantic import ValidationError
from flask_cors import CORS

from postdetection import handle_predict, handle_extract, handle_extract_and_predict
from predetection import handle_predetection
from dtos import Article, HTMLPayload, LatencyEntry
from utils import display_dict
from config import Config
import db

import os
import time

app = Flask(__name__)
CORS(app)

db.init_db()


def _record_backend_time(type_: str, site: str, start: float) -> None:
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    try:
        db.insert_time(type_, "backend", site, elapsed_ms)
    except Exception as e:
        app.logger.error(f"Failed to record backend latency: {e}")


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
    start = time.perf_counter()
    site = ""
    detection_type = "post"
    try:
        if Config.RESTRICTED and not validate_access(request):
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        app.logger.info(f"Received request for /extract_and_predict endpoint with payload {display_dict(data)}")
        html_payload = HTMLPayload(**data)
        site = html_payload.url
        generate_spoiler = data.get("generateSpoiler", True)
        detection_type = "spoiler" if generate_spoiler else "post"
        prediction = handle_extract_and_predict(html_payload, generate_spoiler=generate_spoiler)

        response = jsonify(prediction.model_dump())
        _record_backend_time(detection_type, site, start)
        return response
    except (ValidationError, Exception) as e:
        return jsonify({"error": str(e)}), 400

@app.route("/predetect", methods=["POST"])
async def detect():
    if request.method == 'OPTIONS':
        return '', 204
    start = time.perf_counter()
    site = ""
    try:
        if Config.RESTRICTED and not validate_access(request):
            return jsonify({"error": "Unauthorized"}), 403
        data = request.get_json()
        app.logger.info(f"Received request for /predetect endpoint with payload {display_dict(data)}")
        html_payload = HTMLPayload(**data)
        site = html_payload.url
        prediction = await handle_predetection(html_payload)
        response = jsonify(prediction.model_dump())
        _record_backend_time("pre", site, start)
        return response
    except (ValidationError, Exception) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/latency", methods=["POST", "OPTIONS"])
def latency_add():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.get_json()
        entry = LatencyEntry(**data)
        db.insert_time(entry.type, entry.location, entry.site, entry.time)
        return jsonify({"status": "ok"})
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
