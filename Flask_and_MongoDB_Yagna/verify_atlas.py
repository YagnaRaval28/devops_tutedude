"""
Checks the MongoDB Atlas connection defined in .env.

Run with:  python verify_atlas.py

Pings the cluster, writes a test document, reads it back, deletes it, and
prints the current document count. Good screenshot material for the report.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConfigurationError, OperationFailure, ServerSelectionTimeoutError

# Load .env from next to this file, not from the current working directory,
# so the script works no matter which folder it is run from.
load_dotenv(Path(__file__).resolve().parent / ".env")

URI = os.getenv("MONGO_URI", "")
DB = os.getenv("MONGO_DB", "tutedude_assignment")
COLL = os.getenv("MONGO_COLLECTION", "registrations")


def mask(uri):
    """Hide the password so the output is safe to screenshot."""
    if "@" not in uri or "//" not in uri:
        return uri
    scheme, rest = uri.split("//", 1)
    creds, host = rest.split("@", 1)
    user = creds.split(":")[0] if ":" in creds else creds
    return f"{scheme}//{user}:*****@{host}"


def main():
    if not URI:
        print("[FAIL] MONGO_URI is not set.")
        print("       Copy .env.example to .env and paste your Atlas connection string.")
        return 1

    print(f"URI       : {mask(URI)}")
    print(f"Database  : {DB}")
    print(f"Collection: {COLL}\n")

    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=8000)

        client.admin.command("ping")
        print("[PASS] Ping succeeded - Atlas cluster is reachable.")

        coll = client[DB][COLL]

        res = coll.insert_one({
            "_connection_test": True,
            "created_at": datetime.now(timezone.utc),
        })
        print(f"[PASS] Write OK  - inserted test document {res.inserted_id}")

        found = coll.find_one({"_id": res.inserted_id})
        print(f"[PASS] Read OK   - read the document back ({'found' if found else 'MISSING'})")

        coll.delete_one({"_id": res.inserted_id})
        print("[PASS] Delete OK - test document cleaned up")

        print(f"\nDocuments currently in '{DB}.{COLL}': {coll.count_documents({})}")
        print("\nAtlas connection is working. You can run:  python app.py")
        return 0

    except ServerSelectionTimeoutError as exc:
        print(f"[FAIL] Could not reach the cluster.\n       {exc}")
        # An SSL/TLS failure means the connection reached Atlas but was cut
        # during negotiation, which is a different problem from not being
        # allowed to connect at all.
        if "SSL" in str(exc) or "TLS" in str(exc):
            print("\n       The TLS handshake failed, so the connection reached")
            print("       Atlas but was interrupted. Usual causes:")
            print("         - Antivirus / firewall with HTTPS or SSL scanning enabled")
            print("         - A school, office or public network that inspects traffic")
            print("         - A VPN or proxy interfering with port 27017")
            print("\n       Try a different network (a mobile hotspot is the quickest")
            print("       test) or temporarily disable SSL scanning in your antivirus.")
        else:
            print("\n       Most common cause: your IP is not whitelisted.")
            print("       Fix in Atlas -> Network Access -> Add IP Address.")
            print("       Also check the cluster is not paused in Atlas -> Database.")
    except OperationFailure as exc:
        print(f"[FAIL] Authentication or permission error.\n       {exc}")
        print("\n       Check the username/password in MONGO_URI.")
        print("       URL-encode special characters (@ -> %40, # -> %23, : -> %3A).")
    except ConfigurationError as exc:
        print(f"[FAIL] The connection string looks malformed.\n       {exc}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
