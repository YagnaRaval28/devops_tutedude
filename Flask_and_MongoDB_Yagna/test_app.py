"""
Self-contained checks for every assignment requirement.

Run with:  python test_app.py

MongoDB is faked here so the success/error paths can both be proven without
needing live Atlas credentials. Use verify_atlas.py for the real connection.
"""

import json
import sys

from pymongo.errors import ServerSelectionTimeoutError

import app as flask_app

PASS, FAIL = [], []


def check(label, condition, detail=""):
    (PASS if condition else FAIL).append(label)
    mark = "PASS" if condition else "FAIL"
    print(f"[{mark}] {label}" + (f"  -> {detail}" if detail else ""))


class FakeResult:
    inserted_id = "652f1a9c8d4e2b0011aa33bc"


class FakeCollection:
    """Records inserts; can be told to raise to simulate a DB failure."""

    def __init__(self, raises=None):
        self.raises = raises
        self.docs = []

    def insert_one(self, doc):
        if self.raises:
            raise self.raises
        self.docs.append(doc)
        return FakeResult()


def main():
    client = flask_app.app.test_client()

    print("\n=== Task 1: JSON API route ===")
    resp = client.get("/api")
    check("GET /api returns HTTP 200", resp.status_code == 200, f"got {resp.status_code}")
    check(
        "GET /api Content-Type is application/json",
        resp.headers["Content-Type"].startswith("application/json"),
        resp.headers["Content-Type"],
    )
    payload = resp.get_json()
    check("GET /api returns a JSON list", isinstance(payload, list), type(payload).__name__)
    check("List is non-empty", len(payload) > 0, f"{len(payload)} records")

    on_disk = json.load(open(flask_app.DATA_FILE, encoding="utf-8"))
    check("Response matches the backend data file exactly", payload == on_disk)

    print("\n=== Task 2a: form page renders ===")
    resp = client.get("/form")
    check("GET /form returns HTTP 200", resp.status_code == 200, f"got {resp.status_code}")
    check("Form page contains the name field", b'name="name"' in resp.data)
    check("Course dropdown is populated from the data file", b"DevOps Fundamentals" in resp.data)

    print("\n=== Task 2b: SUCCESS path -> redirect ===")
    fake = FakeCollection()
    flask_app.get_collection = lambda: fake

    resp = client.post(
        "/form",
        data={
            "name": "Yagna Patel",
            "email": "yagna@example.com",
            "phone": "9876543210",
            "course": "DevOps Fundamentals",
            "message": "Excited to learn!",
        },
    )
    check("Valid submit returns HTTP 302 redirect", resp.status_code == 302, f"got {resp.status_code}")
    check("Redirect target is /success", "/success" in resp.headers.get("Location", ""),
          resp.headers.get("Location", ""))
    check("Exactly one document was inserted", len(fake.docs) == 1, f"{len(fake.docs)} inserted")
    if fake.docs:
        doc = fake.docs[0]
        check("Inserted document keeps the submitted name", doc["name"] == "Yagna Patel", doc["name"])
        check("Inserted document has a submitted_at timestamp", "submitted_at" in doc)

    resp = client.get("/success?record_id=abc123")
    check("Success page shows 'Data submitted successfully'",
          b"Data submitted successfully" in resp.data)

    print("\n=== Task 2c: ERROR path -> same page, no redirect ===")
    cases = [
        ("missing required fields", {"name": "", "email": "", "course": ""},
         b"required"),
        ("invalid email", {"name": "Yagna Patel", "email": "not-an-email",
                           "course": "DevOps Fundamentals"}, b"not a valid email"),
        ("short name", {"name": "Yo", "email": "a@b.com",
                        "course": "DevOps Fundamentals"}, b"at least 3 characters"),
        ("bad phone", {"name": "Yagna Patel", "email": "a@b.com", "phone": "123",
                       "course": "DevOps Fundamentals"}, b"10 digits"),
    ]
    for label, data, expected in cases:
        resp = client.post("/form", data=data)
        check(f"[{label}] no redirect (status {resp.status_code})", resp.status_code != 302)
        check(f"[{label}] error shown on the same page", expected in resp.data)

    resp = client.post("/form", data={"name": "Yagna Patel", "email": "yagna@example.com",
                                      "course": "DevOps Fundamentals", "phone": "9876543210"})
    check("Entered values are preserved after an error",
          b"Yagna Patel" in resp.data or resp.status_code == 302)

    print("\n=== Task 2d: database failure -> same page, no redirect ===")
    flask_app.get_collection = lambda: FakeCollection(
        raises=ServerSelectionTimeoutError("connection refused")
    )
    resp = client.post("/form", data={"name": "Yagna Patel", "email": "yagna@example.com",
                                      "course": "DevOps Fundamentals"})
    check("DB outage does not redirect", resp.status_code != 302, f"got {resp.status_code}")
    check("DB outage shows an error on the same page", b"Could not reach MongoDB Atlas" in resp.data)

    print("\n=== Extra routes ===")
    resp = client.get("/")
    check("GET / returns HTTP 200", resp.status_code == 200, f"got {resp.status_code}")
    resp = client.get("/no-such-page")
    check("Unknown URL returns a 404 page", resp.status_code == 404, f"got {resp.status_code}")

    total = len(PASS) + len(FAIL)
    print(f"\n{'=' * 52}")
    print(f"RESULT: {len(PASS)}/{total} checks passed, {len(FAIL)} failed")
    if FAIL:
        for name in FAIL:
            print(f"  FAILED: {name}")
    print("=" * 52)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
