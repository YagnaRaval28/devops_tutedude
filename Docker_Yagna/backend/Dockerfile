# ---- Flask backend ----
FROM python:3.12-slim

# Do not buffer stdout/stderr, so logs appear in `docker compose logs`
# immediately instead of being held until the buffer flushes.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy requirements first: this layer is cached and only rebuilt when the
# dependencies change, so editing app.py does not reinstall packages.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as a non-root user rather than root.
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')"

# gunicorn rather than the Flask development server, which prints a warning
# and is not built for anything beyond local debugging.
#
# A single worker on purpose: submissions are held in memory, and each
# gunicorn worker is its own process with its own copy of that list. With
# two workers a write and a later read can land on different workers, so
# the data appears to vanish. A real deployment would use a database and
# could then scale the workers freely.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "app:app"]
