# Flask & MongoDB Atlas — DevOps Assignment

A Flask application with a JSON API route backed by a data file, and a
frontend form that stores submissions in MongoDB Atlas with proper success
and error handling.

## Features

| Requirement | Implementation |
|---|---|
| Task 1 — `/api` returns a JSON list | `GET /api` reads `data/courses.json` from disk and returns it via `jsonify` |
| Task 2 — form inserts into Atlas | `POST /form` validates input and calls `insert_one()` on the Atlas collection |
| On success — redirect to another page | `redirect(url_for("success"))` → `/success` shows "Data submitted successfully" |
| On error — show error, no redirect | The same `form.html` is re-rendered with the error message and the user's input preserved |

## Routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Home page listing the data served by `/api` |
| GET | `/api` | **Task 1** — returns the backend JSON list |
| GET | `/form` | **Task 2** — the registration form |
| POST | `/form` | Validates and inserts into MongoDB Atlas |
| GET | `/success` | Confirmation page (redirect target) |
| GET | `/records` | Reads documents back from Atlas (proof of storage) |

## Project structure

```
Flask_and_MongoDB_Yagna/
├── app.py                 # Flask application (all routes)
├── verify_atlas.py        # Standalone Atlas connection checker
├── test_app.py            # Automated checks for every requirement
├── requirements.txt
├── .env.example           # Template for the connection string
├── .gitignore             # Keeps .env out of Git
├── data/
│   └── courses.json       # Backend data file read by /api
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── form.html          # Renders inline errors
│   ├── success.html       # "Data submitted successfully"
│   ├── records.html
│   └── 404.html
├── static/css/style.css
└── screenshots/
```

## Setup

### 1. Install dependencies

```bash
cd Flask_and_MongoDB_Yagna
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

### 2. Create a MongoDB Atlas cluster

1. Sign up at <https://www.mongodb.com/cloud/atlas/register>.
2. **Build a Database** → choose the free **M0** tier → **Create Deployment**.
3. **Database Access** → *Add New Database User* → username + password
   (*Built-in Role: Read and write to any database*). Save the password.
4. **Network Access** → *Add IP Address*. Use *Add Current IP Address*, or
   `0.0.0.0/0` to allow access from anywhere while testing.
5. **Database** → **Connect** → **Drivers** → **Python** → copy the connection
   string. It looks like:
   `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`

### 3. Configure `.env`

```bash
copy .env.example .env         # Windows
# cp .env.example .env         # macOS / Linux
```

Edit `.env` and paste your string, replacing `<username>` and `<password>`:

```
MONGO_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=tutedude_assignment
MONGO_COLLECTION=registrations
SECRET_KEY=any-long-random-string
FLASK_DEBUG=1
```

> **Password note:** URL-encode special characters — `@` → `%40`,
> `#` → `%23`, `:` → `%3A`, `/` → `%2F`.

### 4. Verify the connection

```bash
python verify_atlas.py
```

Expected output:

```
[PASS] Ping succeeded - Atlas cluster is reachable.
[PASS] Write OK  - inserted test document 6520...
[PASS] Read OK   - read the document back (found)
[PASS] Delete OK - test document cleaned up
```

### 5. Run the app

```bash
python app.py
```

Open <http://127.0.0.1:5000>.

## Testing

```bash
python test_app.py
```

Runs 27 checks covering the API route, the success redirect, every validation
error, and a simulated database outage. MongoDB is mocked, so this runs
without Atlas credentials.

## Verifying Task 1 from the terminal

```bash
curl http://127.0.0.1:5000/api
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Could not reach MongoDB Atlas` | Add your IP under Atlas → Network Access |
| `Authentication failed` | Wrong user/password; URL-encode special characters |
| `MONGO_URI is not set` | Create `.env` from `.env.example` |
| `Port 5000 in use` | Change the port in the `app.run()` call at the bottom of `app.py` |

## Security note

`.env` holds the database password and is listed in `.gitignore`, so it is
never committed. Only `.env.example` (with placeholders) is tracked.
