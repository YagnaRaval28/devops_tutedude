"""
Flask backend for the Docker assignment.

Receives the registration form submitted by the Express frontend, validates
it, and returns a JSON result. The frontend reaches this service by its
Compose service name (http://backend:5000), not by localhost, because each
container has its own network namespace.
"""

import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request

app = Flask(__name__)

COURSES = [
    "DevOps Fundamentals",
    "Docker & Kubernetes",
    "Flask Web Development",
    "Node.js & Express",
    "CI/CD with Jenkins",
]

# Submissions are kept in memory for the lifetime of the container. The
# assignment asks the backend to process the data, not to persist it.
submissions = []


def validate(payload):
    """Return (cleaned, error). error is None when the payload is valid."""
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    course = (payload.get("course") or "").strip()
    phone = (payload.get("phone") or "").strip()
    message = (payload.get("message") or "").strip()

    if not name or not email or not course:
        return None, "Name, Email and Course are required fields."
    if len(name) < 3:
        return None, "Name must be at least 3 characters long."
    if "@" not in email or "." not in email.split("@")[-1]:
        return None, f"'{email}' is not a valid email address."
    if phone and (not phone.isdigit() or len(phone) != 10):
        return None, "Phone number must be exactly 10 digits."
    if course not in COURSES:
        return None, f"'{course}' is not one of the available courses."

    return {
        "name": name,
        "email": email,
        "course": course,
        "phone": phone,
        "message": message,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }, None


@app.route("/health")
def health():
    """Used by the Compose healthcheck and by the frontend status badge."""
    return jsonify({"status": "healthy", "service": "flask-backend"})


@app.route("/api/courses")
def api_courses():
    """The course list the frontend renders in its dropdown."""
    return jsonify(COURSES)


@app.route("/api/submit", methods=["POST"])
def api_submit():
    """Handle the form submission forwarded by the Express frontend."""
    payload = request.get_json(silent=True) or request.form.to_dict()

    cleaned, error = validate(payload)
    if error:
        return jsonify({"success": False, "error": error}), 400

    cleaned["id"] = len(submissions) + 1
    submissions.append(cleaned)

    return jsonify({
        "success": True,
        "message": "Data submitted successfully",
        "data": cleaned,
    }), 201


@app.route("/api/submissions")
def api_submissions():
    """Return everything processed so far, newest first."""
    return jsonify({"count": len(submissions), "submissions": submissions[::-1]})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",  # must bind 0.0.0.0, not 127.0.0.1, to be reachable
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
