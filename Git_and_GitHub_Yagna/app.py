"""
Flask project for the Git & GitHub assignment.

Base version: home page plus the /api route backed by data/courses.json.
The To-Do page and the /submittodoitem route are added later on the
master_1 and master_2 branches.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "courses.json"

load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")


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


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
