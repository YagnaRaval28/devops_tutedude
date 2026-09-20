"""
Flask project for the Git & GitHub assignment.

Base version: home page plus the /api route backed by data/courses.json.
The To-Do page and the /submittodoitem route are added later on the
master_1 and master_2 branches.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from flask import Flask, jsonify, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "courses.json"

load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "tutedude_git_assignment")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "todo_items")

# One client is created at import time and reused; PyMongo keeps its own
# connection pool, so a client per request would be wasteful.
mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)


def get_todo_collection():
    return mongo_client[MONGO_DB][MONGO_COLLECTION]


def read_courses():
    """Read the backend data file served by /api."""
    with open(DATA_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


@app.route("/")
def home():
    return render_template("index.html", courses=read_courses())


@app.route("/api")
def api():
    """Return the contents of the backend data file as a JSON list."""
    try:
        return jsonify(read_courses())
    except FileNotFoundError:
        return jsonify({"error": f"Data file not found: {DATA_FILE.name}"}), 500
    except json.JSONDecodeError as exc:
        return jsonify({"error": f"Data file is not valid JSON: {exc}"}), 500


@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():
    """Accept itemName and itemDescription and store them in MongoDB."""
    item_name = request.form.get("itemName", "").strip()
    item_description = request.form.get("itemDescription", "").strip()

    if not item_name or not item_description:
        return jsonify({"error": "itemName and itemDescription are required."}), 400

    document = {
        "itemName": item_name,
        "itemDescription": item_description,
        "created_at": datetime.now(timezone.utc),
    }

    try:
        result = get_todo_collection().insert_one(document)
    except ServerSelectionTimeoutError:
        return jsonify({"error": "Could not reach MongoDB."}), 503
    except PyMongoError as exc:
        return jsonify({"error": f"Database error: {exc}"}), 500

    return jsonify({
        "message": "To-Do item stored successfully",
        "id": str(result.inserted_id),
        "itemName": item_name,
        "itemDescription": item_description,
    }), 201


@app.route("/todoitems")
def todo_items():
    """Return the stored To-Do items, proving they reached the database."""
    try:
        docs = list(get_todo_collection().find().sort("created_at", -1).limit(25))
    except (PyMongoError, ServerSelectionTimeoutError) as exc:
        return jsonify({"error": str(exc)}), 503

    for d in docs:
        d["_id"] = str(d["_id"])
        d["created_at"] = d["created_at"].isoformat() if d.get("created_at") else None
    return jsonify(docs)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
