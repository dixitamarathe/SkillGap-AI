
import os
import tempfile

import pdfplumber
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

from analyzer import ROLE_SKILLS, analyze_resume


app = Flask(__name__)

# Allow the frontend to call this API during local development.
CORS(app)

# Maximum upload size: 10 MB.
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_ROLES = list(ROLE_SKILLS.keys())


@app.get("/")
def home():
    return jsonify({
        "message": "SkillGap AI API is running.",
        "supported_roles": ALLOWED_ROLES,
    })


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/analyze")
def analyze():
    if "resume" not in request.files:
        return jsonify({
            "error": "Please upload a PDF resume."
        }), 400

    resume = request.files["resume"]
    job_role = request.form.get("job_role", "").strip()

    if not resume.filename:
        return jsonify({"error": "No file selected."}), 400

    if not resume.filename.lower().endswith(".pdf"):
        return jsonify({
            "error": "Only PDF files are supported."
        }), 400

    if job_role not in ALLOWED_ROLES:
        return jsonify({
            "error": "Please select a valid target job role."
        }), 400

    # Use a temporary file instead of permanently storing the resume.
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False
        ) as temporary_file:
            temporary_path = temporary_file.name
            resume.save(temporary_path)

        with pdfplumber.open(temporary_path) as pdf:
            if not pdf.pages:
                return jsonify({
                    "error": "The PDF contains no pages."
                }), 400

            extracted_pages = [
                page.extract_text() or ""
                for page in pdf.pages
            ]

        resume_text = "\n".join(extracted_pages).strip()

        if not resume_text:
            return jsonify({
                "error": (
                    "No readable text was found. "
                    "This prototype needs a text-based PDF, not a scanned image."
                )
            }), 400

        results = analyze_resume(resume_text, job_role)
        return jsonify(results), 200

    except Exception:
        app.logger.exception("Resume analysis failed.")
        return jsonify({
            "error": (
                "We couldn't process this PDF. "
                "Please try a valid, text-based PDF."
            )
        }), 500

    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)


@app.errorhandler(RequestEntityTooLarge)
def file_too_large(_error):
    return jsonify({
        "error": "File exceeds the 10 MB upload limit."
    }), 413


if __name__ == "__main__":
    # Local development only. Production uses a WSGI server such as Gunicorn.
    app.run(host="127.0.0.1", port=5000, debug=False)
