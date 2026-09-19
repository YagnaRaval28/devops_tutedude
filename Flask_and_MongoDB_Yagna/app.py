"""
Flask & MongoDB Atlas assignment.

Task 1 : GET /api  -> reads data/courses.json from disk and returns it as JSON.
Task 2 : GET/POST /form -> inserts the submitted data into MongoDB Atlas.
         On success -> redirect to /success ("Data submitted successfully").
         On error   -> re-render the same page with the error, no redirect.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "courses.json"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB = os.getenv("MONGO_DB", "tutedude_assignment")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "registrations")

# A single client is created at import time and reused for every request.
# PyMongo maintains its own connection pool, so creating a client per request
# would be wasteful. serverSelectionTimeoutMS keeps a bad URI from hanging
# the request for the default 30 seconds.
if MONGO_URI:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
else:
    mongo_client = None


def get_collection():
    """Return the Atlas collection, raising a readable error if unconfigured."""
    if mongo_client is None:
        raise RuntimeError(
            "MONGO_URI is not set. Copy .env.example to .env and add your "
            "MongoDB Atlas connection string."
        )
    return mongo_client[MONGO_DB][MONGO_COLLECTION]


def read_courses():
    """Task 1: read the backend data file from disk on every request."""
    with open(DATA_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def validate(form):
    """Return (cleaned_data, error_message). error_message is None when valid."""
    name = form.get("name", "").strip()
    email = form.get("email", "").strip()
    course = form.get("course", "").strip()
    phone = form.get("phone", "").strip()
    message = form.get("message", "").strip()

    if not name or not email or not course:
        return None, "Name, Email and Course are required fields."
    if len(name) < 3:
        return None, "Name must be at least 3 characters long."
    if "@" not in email or "." not in email.split("@")[-1]:
        return None, f"'{email}' is not a valid email address."
    if phone and (not phone.isdigit() or len(phone) != 10):
        return None, "Phone number must be exactly 10 digits."

    cleaned = {
        "name": name,
        "email": email,
        "course": course,
        "phone": phone,
        "message": message,
        "submitted_at": datetime.now(timezone.utc),
    }
    return cleaned, None


# --------------------------------------------------------------------------
# Task 1 : JSON API route
# --------------------------------------------------------------------------
@app.route("/api")
def api():
    """Read the backend file and send its contents back as a JSON list."""
    try:
        courses = read_courses()
    except FileNotFoundError:
        return jsonify({"error": f"Data file not found: {DATA_FILE.name}"}), 500
    except json.JSONDecodeError as exc:
        return jsonify({"error": f"Data file is not valid JSON: {exc}"}), 500

    return jsonify(courses)


# --------------------------------------------------------------------------
# Task 2 : Frontend form -> MongoDB Atlas
# --------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", courses=read_courses())


@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "GET":
        return render_template("form.html", courses=read_courses(), data={})

    cleaned, error = validate(request.form)

    # Validation failure -> same page, no redirect (assignment requirement 4).
    if error:
        return (
            render_template(
                "form.html",
                courses=read_courses(),
                data=request.form,
                error=error,
            ),
            400,
        )

    try:
        result = get_collection().insert_one(cleaned)
    except ServerSelectionTimeoutError:
        return (
            render_template(
                "form.html",
                courses=read_courses(),
                data=request.form,
                error=(
                    "Could not reach MongoDB Atlas. Check your internet "
                    "connection and make sure your IP is whitelisted under "
                    "Atlas -> Network Access."
                ),
            ),
            503,
        )
    except (PyMongoError, RuntimeError) as exc:
        return (
            render_template(
                "form.html",
                courses=read_courses(),
                data=request.form,
                error=f"Database error: {exc}",
            ),
            500,
        )

    # Success -> redirect to a different page (assignment requirement 3).
    return redirect(url_for("success", record_id=str(result.inserted_id)))


@app.route("/success")
def success():
    return render_template("success.html", record_id=request.args.get("record_id"))


@app.route("/records")
def records():
    """Extra: proves the documents really landed in Atlas."""
    try:
        docs = list(get_collection().find().sort("submitted_at", -1).limit(25))
    except (PyMongoError, RuntimeError) as exc:
        return render_template("records.html", rows=[], error=str(exc)), 500

    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return render_template("records.html", rows=docs, error=None)


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
