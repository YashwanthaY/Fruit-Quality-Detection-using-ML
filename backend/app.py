"""
FreshSense — app.py (CLEAN)
Flask REST API — no duplicate routes
"""

import os
import time
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from predict import predict_from_image, predict_from_manual

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://freshsense-app.netlify.app"}})
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

# Upload folder inside backend
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name":       "FreshSense API",
        "version":    "2.0.0",
        "status":     "running",
        "concurrent": "unlimited (stateless REST)",
        "endpoints":  {
            "GET  /":              "API info",
            "GET  /health":        "Health check",
            "POST /predict":       "Image upload → quality result",
            "POST /predict-manual":"JSON attributes → quality result"
        }
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": time.time()})


@app.route("/predict", methods=["POST"])
def predict_image():
    if "image" not in request.files:
        return jsonify({"error": "No file attached. Use form key 'image'."}), 400

    file = request.files["image"]
    if not file or file.filename == "":
        return jsonify({"error": "Empty file."}), 400

    allowed = {"jpg", "jpeg", "png", "webp", "bmp"}
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    if ext not in allowed:
        return jsonify({"error": f"Unsupported type: {ext}"}), 400

    tmp_path = os.path.join(UPLOAD_DIR, f"img_{uuid.uuid4().hex}.{ext}")

    try:
        file.save(tmp_path)

        if not os.path.exists(tmp_path):
            return jsonify({"error": "File save failed"}), 500

        start  = time.perf_counter()
        result = predict_from_image(tmp_path)
        result["analysis_time_seconds"] = round(time.perf_counter() - start, 3)
        return jsonify(result), 200

    except Exception as exc:
        app.logger.error(f"Prediction error: {exc}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500

    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except:
            pass


@app.route("/predict-manual", methods=["POST"])
def predict_manual():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required."}), 400

    required = ["fruit_type", "color", "texture", "smell", "days_since_harvest"]
    missing  = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    try:
        start  = time.perf_counter()
        result = predict_from_manual(data)
        result["analysis_time_seconds"] = round(time.perf_counter() - start, 3)
        return jsonify(result), 200

    except Exception as exc:
        app.logger.error(f"Manual prediction error: {exc}")
        return jsonify({"error": str(exc)}), 500


@app.errorhandler(413)
def too_large(_e):
    return jsonify({"error": "File too large. Max 20MB."}), 413


if __name__ == "__main__":
    print("\n🌿  FreshSense API v2.0 — starting...")
    print("    Stateless REST  |  Safe for unlimited concurrent users")
    print("    → http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)