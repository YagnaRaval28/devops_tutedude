# Flask & MongoDB — Assignment Documentation

**Name:** Yagna
**Course:** DevOps
**Assignment:** Flask & MongoDB
**GitHub repository:** `<paste your repository link here>`

---

## Objective

Build a Flask application with a JSON API route and a frontend form that
stores submitted data in MongoDB Atlas, with proper success and error
handling.

---

## Tech stack

| Component | Version | Purpose |
|---|---|---|
| Python | 3.12.4 | Runtime |
| Flask | 3.0.3 | Web framework |
| PyMongo | 4.8.0 | MongoDB driver |
| python-dotenv | 1.0.1 | Loads credentials from `.env` |
| MongoDB Atlas | M0 free tier | Cloud database |

---

## Project structure

```
Flask_and_MongoDB_Yagna/
├── app.py                 # Flask application (all routes)
├── verify_atlas.py        # Atlas connection checker
├── test_app.py            # Automated requirement checks
├── requirements.txt
├── .env.example
├── .gitignore
├── data/courses.json      # Backend data file read by /api
├── templates/             # base, index, form, success, records, 404
├── static/css/style.css
└── screenshots/
```

---

## Environment setup

### Commands

```bash
cd Flask_and_MongoDB_Yagna
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Installed packages

```
Flask==3.0.3
pymongo==4.8.0
python-dotenv==1.0.1
dnspython==2.6.1
```

> **📸 Screenshot 1:** Terminal showing `pip install -r requirements.txt`
> completing successfully.

---

## MongoDB Atlas setup

1. Created a free **M0** cluster at <https://cloud.mongodb.com>.
2. **Database Access** → added a database user with the
   *Read and write to any database* role.
3. **Network Access** → whitelisted my IP address.
4. **Connect → Drivers → Python** → copied the connection string.
5. Saved the string in `.env` (which is git-ignored, so the password is
   never committed):

```
MONGO_URI=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=tutedude_assignment
MONGO_COLLECTION=registrations
```

> **📸 Screenshot 2:** Atlas dashboard showing the running cluster.
>
> **📸 Screenshot 3:** Atlas → Network Access showing the whitelisted IP.

### Verifying the connection

```bash
python verify_atlas.py
```

Output:

```
[PASS] Ping succeeded - Atlas cluster is reachable.
[PASS] Write OK  - inserted test document 6520a1b2c3d4e5f600112233
[PASS] Read OK   - read the document back (found)
[PASS] Delete OK - test document cleaned up

Documents currently in 'tutedude_assignment.registrations': 0
```

> **📸 Screenshot 4:** Terminal output of `python verify_atlas.py`.

---

## Task 1 — JSON API route

### Requirement

> Create a Flask application with an `/api` route. When this route is
> accessed, it should return a JSON list. The data should be stored in a
> backend file, read from it, and sent as a response.

### Backend data file — `data/courses.json`

```json
[
  {
    "id": 1,
    "title": "DevOps Fundamentals",
    "instructor": "Tutedude Mentor",
    "duration_weeks": 8,
    "level": "Beginner",
    "tags": ["linux", "git", "ci-cd"]
  }
]
```

*(5 records total — abbreviated here.)*

### Implementation — `app.py`

```python
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "courses.json"


def read_courses():
    """Task 1: read the backend data file from disk on every request."""
    with open(DATA_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


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
```

**How it satisfies the requirement**

- The data lives in a **backend file** (`data/courses.json`), not hardcoded.
- It is **read from disk** on each request via `read_courses()`.
- It is **sent as a JSON response** using `jsonify`, which sets
  `Content-Type: application/json`.
- A missing or corrupt file returns a clean JSON error instead of crashing.

### Verification

```bash
curl -i http://127.0.0.1:5000/api
```

```
HTTP/1.1 200 OK
Server: Werkzeug/3.0.3 Python/3.12.4
Content-Type: application/json
Content-Length: 735

[{"duration_weeks":8,"id":1,"instructor":"Tutedude Mentor","level":"Beginner",
"tags":["linux","git","ci-cd"],"title":"DevOps Fundamentals"}, ... ]
```

> **📸 Screenshot 5:** Browser at `http://127.0.0.1:5000/api` showing the JSON list.
>
> **📸 Screenshot 6:** Terminal showing the `curl` command and its JSON output.

---

## Task 2 — Frontend form with MongoDB Atlas

### Requirement

> Create a form on the frontend that, when submitted, inserts data into
> MongoDB Atlas.
> **On success:** redirect to another page displaying "Data submitted successfully".
> **On error:** display the error on the same page without redirection.

### The form — `templates/form.html`

```html
{% if error %}
<div class="alert alert-error">
  <strong>Error:</strong> {{ error }}
</div>
{% endif %}

<form class="form" method="POST" action="{{ url_for('form') }}" novalidate>
  <label for="name">Full Name <span class="req">*</span></label>
  <input type="text" id="name" name="name" value="{{ data.get('name', '') }}">

  <label for="email">Email <span class="req">*</span></label>
  <input type="text" id="email" name="email" value="{{ data.get('email', '') }}">

  <label for="course">Course <span class="req">*</span></label>
  <select id="course" name="course">
    <option value="">-- Select a course --</option>
    {% for c in courses %}
    <option value="{{ c.title }}"
      {% if data.get('course') == c.title %}selected{% endif %}>{{ c.title }}</option>
    {% endfor %}
  </select>

  <button class="btn btn-primary" type="submit">Submit</button>
</form>
```

`novalidate` disables the browser's built-in validation so that the
**server-side** error handling is what actually gets demonstrated.

Each field re-renders `data.get(...)`, so a user's input is preserved when an
error occurs and they do not have to retype everything.

### Validation — `app.py`

```python
def validate(form):
    """Return (cleaned_data, error_message). error_message is None when valid."""
    name = form.get("name", "").strip()
    email = form.get("email", "").strip()
    course = form.get("course", "").strip()
    phone = form.get("phone", "").strip()

    if not name or not email or not course:
        return None, "Name, Email and Course are required fields."
    if len(name) < 3:
        return None, "Name must be at least 3 characters long."
    if "@" not in email or "." not in email.split("@")[-1]:
        return None, f"'{email}' is not a valid email address."
    if phone and (not phone.isdigit() or len(phone) != 10):
        return None, "Phone number must be exactly 10 digits."

    cleaned = {
        "name": name, "email": email, "course": course,
        "phone": phone, "message": message,
        "submitted_at": datetime.now(timezone.utc),
    }
    return cleaned, None
```

### The POST handler

```python
@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "GET":
        return render_template("form.html", courses=read_courses(), data={})

    cleaned, error = validate(request.form)

    # Validation failure -> same page, no redirect (requirement 4).
    if error:
        return render_template("form.html", courses=read_courses(),
                               data=request.form, error=error), 400

    try:
        result = get_collection().insert_one(cleaned)
    except ServerSelectionTimeoutError:
        return render_template("form.html", courses=read_courses(),
                               data=request.form,
                               error="Could not reach MongoDB Atlas. ..."), 503
    except (PyMongoError, RuntimeError) as exc:
        return render_template("form.html", courses=read_courses(),
                               data=request.form,
                               error=f"Database error: {exc}"), 500

    # Success -> redirect to a different page (requirement 3).
    return redirect(url_for("success", record_id=str(result.inserted_id)))
```

**The key distinction**

| Outcome | Response | Why |
|---|---|---|
| Success | `redirect(...)` → HTTP 302 → `/success` | Requirement 3 |
| Validation error | `render_template("form.html", error=...)` → HTTP 400 | Requirement 4 — same page |
| Database error | `render_template("form.html", error=...)` → HTTP 500/503 | Requirement 4 — same page |

Only the success branch calls `redirect()`. Every failure path calls
`render_template()` on the *same* template, so the URL stays `/form`.

### Success page — `templates/success.html`

```html
<div class="success-box">
  <div class="tick">&#10004;</div>
  <h1>Data submitted successfully</h1>
  <p>Your details have been stored in MongoDB Atlas.</p>
  {% if record_id %}
  <p class="muted">Inserted document ID: <code>{{ record_id }}</code></p>
  {% endif %}
</div>
```

---

## Testing and results

### Success path

1. Opened `http://127.0.0.1:5000/form`.
2. Filled in valid details and clicked **Submit**.
3. The browser redirected to `/success` showing **"Data submitted successfully"**.

> **📸 Screenshot 7:** The filled-in form before submitting.
>
> **📸 Screenshot 8:** The `/success` page — note the URL changed to `/success`.
>
> **📸 Screenshot 9:** Atlas → Browse Collections showing the inserted document.
>
> **📸 Screenshot 10:** The `/records` page listing records read back from Atlas.

### Error path (no redirect)

Submitting an invalid email keeps the user on `/form`:

```bash
curl -i -X POST http://127.0.0.1:5000/form \
  -d "name=Yagna Patel" -d "email=bademail" -d "course=DevOps Fundamentals"
```

```
HTTP/1.1 400 BAD REQUEST
Content-Type: text/html; charset=utf-8
```

The response is the form page itself with the error banner rendered — there
is **no `Location` header**, which proves no redirect occurred.

| Input | Error shown on the same page |
|---|---|
| Empty required fields | Name, Email and Course are required fields. |
| Name = "Yo" | Name must be at least 3 characters long. |
| Email = "bademail" | 'bademail' is not a valid email address. |
| Phone = "123" | Phone number must be exactly 10 digits. |
| Atlas unreachable | Could not reach MongoDB Atlas. Check your internet connection… |

> **📸 Screenshot 11:** The form showing a validation error, with the URL
> still `/form` and the entered values preserved.
>
> **📸 Screenshot 12:** The form showing a database connection error.

### Automated test suite

```bash
python test_app.py
```

```
=== Task 1: JSON API route ===
[PASS] GET /api returns HTTP 200  -> got 200
[PASS] GET /api Content-Type is application/json  -> application/json
[PASS] GET /api returns a JSON list  -> list
[PASS] List is non-empty  -> 5 records
[PASS] Response matches the backend data file exactly

=== Task 2a: form page renders ===
[PASS] GET /form returns HTTP 200  -> got 200
[PASS] Form page contains the name field
[PASS] Course dropdown is populated from the data file

=== Task 2b: SUCCESS path -> redirect ===
[PASS] Valid submit returns HTTP 302 redirect  -> got 302
[PASS] Redirect target is /success  -> /success?record_id=652f1a9c8d4e2b0011aa33bc
[PASS] Exactly one document was inserted  -> 1 inserted
[PASS] Inserted document keeps the submitted name  -> Yagna Patel
[PASS] Inserted document has a submitted_at timestamp
[PASS] Success page shows 'Data submitted successfully'

=== Task 2c: ERROR path -> same page, no redirect ===
[PASS] [missing required fields] no redirect (status 400)
[PASS] [missing required fields] error shown on the same page
[PASS] [invalid email] no redirect (status 400)
[PASS] [invalid email] error shown on the same page
[PASS] [short name] no redirect (status 400)
[PASS] [short name] error shown on the same page
[PASS] [bad phone] no redirect (status 400)
[PASS] [bad phone] error shown on the same page
[PASS] Entered values are preserved after an error

=== Task 2d: database failure -> same page, no redirect ===
[PASS] DB outage does not redirect  -> got 503
[PASS] DB outage shows an error on the same page

=== Extra routes ===
[PASS] GET / returns HTTP 200  -> got 200
[PASS] Unknown URL returns a 404 page  -> got 404

====================================================
RESULT: 27/27 checks passed, 0 failed
====================================================
```

> **📸 Screenshot 13:** Terminal output of `python test_app.py` showing 27/27 passed.

---

## Document stored in MongoDB Atlas

```json
{
  "_id": { "$oid": "6520a1b2c3d4e5f600112233" },
  "name": "Yagna Patel",
  "email": "yagna@example.com",
  "course": "DevOps Fundamentals",
  "phone": "9876543210",
  "message": "Excited to learn!",
  "submitted_at": { "$date": "2026-09-19T05:12:44.318Z" }
}
```

---

## Design decisions

**A single shared `MongoClient`.** PyMongo maintains its own connection pool,
so the client is created once at import time and reused. Creating one per
request would open a new pool on every submission.

**`serverSelectionTimeoutMS=5000`.** Without it, an unreachable cluster makes
the request hang for PyMongo's 30-second default. Five seconds fails fast
enough to render a helpful error to the user.

**Credentials in `.env`, not in code.** The connection string contains a
database password. `.env` is listed in `.gitignore`; only `.env.example`
with placeholders is committed.

**Specific exception handling.** `ServerSelectionTimeoutError` (network/IP
whitelist) is caught separately from general `PyMongoError` so the error
message can point at the actual cause.

**Server-side validation.** `novalidate` on the form means the browser does
not block submission, so the Flask validation is what runs — which is the
behaviour the assignment asks to demonstrate.

---

## Conclusion

All four requirements are implemented and verified:

1. ✅ `/api` reads a backend data file and returns it as a JSON list.
2. ✅ The frontend form inserts submitted data into MongoDB Atlas.
3. ✅ On success the user is redirected to `/success`, which displays
   "Data submitted successfully".
4. ✅ On error the message is displayed on the same page with no redirection,
   covering both validation failures and database errors.

**GitHub repository:** `<paste your repository link here>`
