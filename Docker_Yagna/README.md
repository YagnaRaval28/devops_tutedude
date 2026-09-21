# Docker — DevOps Assignment

A full-stack application containerized with Docker and Docker Compose: an
Express/Node.js frontend serving a registration form, and a Flask backend
that processes the submissions. The two services talk to each other over a
shared Docker network.

## Architecture

```
                 ┌──────────────────────────────────────────┐
  Browser        │        docker network: app-network        │
    │            │                                           │
    │  :3000     │   ┌────────────────┐   ┌───────────────┐  │
    └───────────────►│    frontend    │──►│    backend    │  │
                 │   │  Express/Node  │   │     Flask     │  │
                 │   │     :3000      │   │     :5000     │  │
                 │   └────────────────┘   └───────────────┘  │
                 │      http://backend:5000                  │
                 └──────────────────────────────────────────┘
```

The frontend reaches the backend at `http://backend:5000` — the Compose
service name, resolved by Docker's internal DNS. `localhost` would not work,
because inside a container `localhost` is that container itself.

## Project structure

```
Docker_Yagna/
├── docker-compose.yaml       # Connects both services on one network
├── .gitignore                # Excludes node_modules, .vscode, .env
├── frontend/                 # Express + EJS
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── package.json
│   ├── server.js             # Forwards form data to the Flask backend
│   ├── views/                # index / success / submissions
│   └── public/css/style.css
├── backend/                  # Flask
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── app.py                # Validates and processes submissions
└── screenshots/
```

## Running it

```bash
cd Docker_Yagna
docker compose up --build
```

Then open <http://localhost:3000>.

| URL | What it does |
|---|---|
| http://localhost:3000 | The registration form |
| http://localhost:3000/submissions | Submissions read back from the backend |
| http://localhost:3000/health | Frontend status, including backend reachability |
| http://localhost:5001/health | The backend directly |
| http://localhost:5001/api/submissions | The backend's raw JSON |

To stop:

```bash
docker compose down
```

## Ports

| Service | Container | Host | Why |
|---|---|---|---|
| frontend | 3000 | 3000 | The page you open |
| backend | 5000 | **5001** | 5000 was already in use on the host machine |

The backend's host port only exists so it can be tested directly with curl.
The frontend never uses it — it talks to the backend over the internal
network on port 5000.

## Docker Hub

```bash
docker login
docker push yagnaraval/docker-assignment-frontend:latest
docker push yagnaraval/docker-assignment-backend:latest
```

- <https://hub.docker.com/r/yagnaraval/docker-assignment-frontend>
- <https://hub.docker.com/r/yagnaraval/docker-assignment-backend>

To run from Docker Hub without building:

```bash
docker pull yagnaraval/docker-assignment-frontend:latest
docker pull yagnaraval/docker-assignment-backend:latest
docker compose up
```

## Implementation notes

**Layer caching.** Both Dockerfiles copy their dependency manifest
(`package*.json`, `requirements.txt`) and install *before* copying the
source. Docker caches each layer, so editing `server.js` or `app.py` does
not trigger a reinstall of every dependency.

**Non-root users.** The backend creates an `appuser`; the frontend uses the
`node` user that `node:alpine` already provides. Running as root inside a
container is an unnecessary risk.

**Healthchecks use `127.0.0.1`, not `localhost`.** In Alpine, `localhost`
resolves to the IPv6 address `::1` first, and a server bound to IPv4
`0.0.0.0` never answers it — the healthcheck fails with "connection
refused" even though the service is running fine.

**`depends_on: condition: service_healthy`.** Plain `depends_on` only waits
for the container to *start*, not to be *ready*. Waiting on the healthcheck
means the frontend never boots against a backend that is not yet accepting
requests.

**One gunicorn worker.** Submissions are held in memory, and each gunicorn
worker is a separate process with its own copy of that list. With two
workers, a write and a later read can land on different workers and the
data appears to vanish. A real deployment would use a database and could
then scale workers freely.

**`.dockerignore`.** Keeps `node_modules`, `.git` and local environment
files out of the build context, which makes builds faster and images
smaller.

## Images

| Image | Base | Size |
|---|---|---|
| `yagnaraval/docker-assignment-frontend` | `node:20-alpine` | ~205 MB |
| `yagnaraval/docker-assignment-backend` | `python:3.12-slim` | ~187 MB |
