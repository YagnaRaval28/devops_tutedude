/**
 * Express frontend for the Docker assignment.
 *
 * Serves the registration form and forwards submissions to the Flask
 * backend. The backend URL comes from BACKEND_URL, which Compose sets to
 * http://backend:5000 - the service name, resolved by Docker's internal
 * DNS. Using localhost would fail, because inside a container localhost
 * is the container itself, not the host or a sibling service.
 */

const path = require("path");
const express = require("express");

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:5000";

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.use(express.static(path.join(__dirname, "public")));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

/** Fetch the course list from the backend, falling back if it is down. */
async function fetchCourses() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/courses`, {
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) throw new Error(`backend returned ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Could not load courses: ${err.message}`);
    return [];
  }
}

app.get("/", async (req, res) => {
  const courses = await fetchCourses();
  res.render("index", {
    courses,
    data: {},
    error: courses.length ? null : "Could not reach the backend service.",
    backendUrl: BACKEND_URL,
  });
});

app.post("/submit", async (req, res) => {
  const courses = await fetchCourses();

  let result;
  try {
    const response = await fetch(`${BACKEND_URL}/api/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req.body),
      signal: AbortSignal.timeout(8000),
    });
    result = await response.json();

    // The backend rejected the data: re-render the form with its message
    // and the values the user typed, so nothing has to be retyped.
    if (!response.ok) {
      return res.status(response.status).render("index", {
        courses,
        data: req.body,
        error: result.error || "The backend rejected the submission.",
        backendUrl: BACKEND_URL,
      });
    }
  } catch (err) {
    return res.status(503).render("index", {
      courses,
      data: req.body,
      error: `Could not reach the backend service: ${err.message}`,
      backendUrl: BACKEND_URL,
    });
  }

  res.render("success", { result: result.data, message: result.message });
});

app.get("/submissions", async (req, res) => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/submissions`, {
      signal: AbortSignal.timeout(5000),
    });
    const payload = await response.json();
    res.render("submissions", { rows: payload.submissions, error: null });
  } catch (err) {
    res.status(503).render("submissions", { rows: [], error: err.message });
  }
});

/** Reports whether this service can see the backend. */
app.get("/health", async (req, res) => {
  let backend = "unreachable";
  try {
    const r = await fetch(`${BACKEND_URL}/health`, {
      signal: AbortSignal.timeout(3000),
    });
    if (r.ok) backend = "healthy";
  } catch {
    /* leave as unreachable */
  }
  res.json({ status: "healthy", service: "express-frontend", backend });
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Frontend listening on port ${PORT}`);
  console.log(`Backend URL: ${BACKEND_URL}`);
});
