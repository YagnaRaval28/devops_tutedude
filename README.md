# DevOps — Tutedude Assignments

Assignment submissions for the Tutedude DevOps course.

| # | Assignment | Folder | Stack |
|---|---|---|---|
| 3 | Flask & MongoDB | [Flask_and_MongoDB_Yagna](./Flask_and_MongoDB_Yagna) | Python, Flask, MongoDB Atlas |

---

## Assignment 3 — Flask & MongoDB

A Flask application with a JSON API route and a frontend form that stores
submitted data in MongoDB Atlas, with proper success and error handling.

- **Task 1** — `GET /api` reads a backend data file and returns it as a JSON list
- **Task 2** — a form that inserts submissions into MongoDB Atlas
  - On success: redirects to a page showing "Data submitted successfully"
  - On error: shows the error on the same page, without redirecting

Setup instructions are in the
[project README](./Flask_and_MongoDB_Yagna/README.md), and the full write-up
with screenshots is in
[DOCUMENTATION.md](./Flask_and_MongoDB_Yagna/DOCUMENTATION.md).

```bash
cd Flask_and_MongoDB_Yagna
pip install -r requirements.txt
cp .env.example .env     # add your MongoDB Atlas connection string
python verify_atlas.py   # check the cluster connection
python app.py
```

---

**Author:** Yagna Raval
