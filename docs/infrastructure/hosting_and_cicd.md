## Hosting & CI/CD

- **Hosting Platform:** The application is currently designed to run on standard VPS hosting (e.g., AWS EC2, DigitalOcean, Linode) or PaaS providers (Heroku, Render) using Gunicorn as the WSGI HTTP Server. The web server routes traffic to the Flask application.
- **CI/CD Pipeline:** Continuous Integration is managed via GitHub Actions (`.github/workflows/ci.yml`).
- **Triggers:** The pipeline triggers on pushes and pull requests to `feature/*`, `develop`, and `master` branches.
- **Workflow:** It checks out the code, sets up Python 3.11, installs dependencies via `requirements.txt`, and runs the `pytest` test suite to prevent regressions.
