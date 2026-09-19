# Screenshot checklist

Save each screenshot in this folder, then paste it into DOCUMENTATION.md at
the matching "Screenshot N" marker.

## Setup
- [ ] **01-pip-install.png** — `pip install -r requirements.txt` completing
- [ ] **02-atlas-cluster.png** — Atlas dashboard with the cluster running
- [ ] **03-atlas-network.png** — Atlas -> Network Access, IP whitelisted
- [ ] **04-verify-atlas.png** — `python verify_atlas.py` all PASS

## Task 1 - JSON API
- [ ] **05-api-browser.png** — browser at `http://127.0.0.1:5000/api`
- [ ] **06-api-curl.png** — `curl http://127.0.0.1:5000/api` in the terminal

## Task 2 - Success path
- [ ] **07-form-filled.png** — the form filled in, before submitting
- [ ] **08-success-page.png** — `/success` page (make sure the URL bar shows `/success`)
- [ ] **09-atlas-document.png** — Atlas -> Browse Collections, the inserted document
- [ ] **10-records-page.png** — `/records` listing data read back from Atlas

## Task 2 - Error path
- [ ] **11-validation-error.png** — error banner, URL still `/form`
- [ ] **12-db-error.png** — database error banner on the same page

## Tests
- [ ] **13-test-suite.png** — `python test_app.py` showing 27/27 passed

---

## How to capture the error screenshots

**Validation error (11)** — submit the form with an invalid email such as
`bademail`. The page reloads with the red error banner and the URL stays
`/form`. Make the URL bar visible in the shot: that is what proves there
was no redirect.

**Database error (12)** — temporarily break the connection so the app
cannot reach Atlas:

1. Open `.env`.
2. Change one character in the cluster hostname inside `MONGO_URI`.
3. Restart `python app.py`, submit a valid form.
4. The error banner appears on the same page.
5. Undo the change to `.env` afterwards.

## Windows screenshot shortcut

`Win + Shift + S` opens Snip & Sketch. The capture goes to the clipboard;
paste it into Paint and save it here with the filename above.
