# Deploying and Updating Application in cPanel

This guide outlines the steps to deploy and update our Flask application on a cPanel hosting environment using Phusion Passenger and GitHub Actions.

## 1. Initial cPanel Setup (Prerequisites)

*Note: This is a critical step that must be done manually before automated deployment works.*

1. **Database Setup**: 
   - Navigate to **MySQL Databases** (or PostgreSQL) in cPanel.
   - Create a new database and a database user.
   - Assign the user to the database with all privileges.
   - Note down the database name, username, and password to construct your `DATABASE_URL`.

2. **Python App Setup**:
   - Navigate to **Setup Python App** (under Software) in cPanel.
   - Click **Create Application**.
   - **Python Version**: Select the appropriate version for the application.
   - **Application Root**: Enter the directory name (e.g., `develop.lineage.joelmuhoho.com`).
   - **Application URL**: Choose the domain/subdomain.
   - **Environment Variables**: Add necessary secrets like `DATABASE_URL`, `SECRET_KEY`, etc.
   - Click **Create**. This will generate a virtual environment and a default `passenger_wsgi.py` file.

## 2. FTP Deployment Configuration

To allow GitHub Actions to upload files to our cPanel server, we need a dedicated FTP account.

1. Navigate to **Files** > **FTP Accounts** in cPanel.
2. Under **Add FTP Account**, fill in the details:
   - **Log In**: Enter a partial username (e.g., `joel`).
   - **Domain**: Select your site domain (e.g., `develop.lineage.joelmuhoho.com`). This makes your full username `joel@develop.lineage.joelmuhoho.com`.
   - **Password**: Enter a strong password.
   - **Directory**: Set this exactly to the Application Root defined earlier (e.g., `develop.lineage.joelmuhoho.com`). *Important: Do not use `public_html` if your app is placed outside of it.*
3. Click **Create FTP Account**.
4. Once created, scroll down to the new account and click **Configure FTP Client**. You will need these details for GitHub Actions:
   - **FTP Username**: `joel@develop.lineage.joelmuhoho.com`
   - **FTP Server**: `ftp.joelmuhoho.com`
   - **Port**: `21`

## 3. GitHub Actions CI/CD Setup

We use GitHub Actions to automatically deploy changes via FTP.

here is an example of github actions cd-to-cpanel file.
```
name: CD for lineage develop to cPanel

on:
  workflow_run:
    workflows:
      - CI for lineage
    types:
      - completed
    branches:
      - develop

jobs:
  deploy-develop-cpanel:
    runs-on: ubuntu-latest
    if: github.event.workflow_run.conclusion == 'success'
    steps:
      - name: Checkout Code
        uses: actions/checkout@v6 # fetches all the code in the current branch

      - name: Checkout tested commit
        if: github.event_name == 'workflow_run' # on workflow run triggered
        uses: actions/checkout@v6 # fetch the tested commit
        with:
          ref: ${{ github.event.workflow_run.head_sha }} # this is the tested commit SHA from CI for lineage workflow

      - name: Trigger Passenger restart
        run: |
          mkdir -p ./tmp # create tmp directory if it doesn't exist
          printf 'restart: %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" > ./tmp/restart.txt # write current date and time to tmp/restart.txt

      - name: Sync Files to cPanel
        uses: SamKirkland/FTP-Deploy-Action@v4.3.5 # FTP deployment action for GitHub Actions
        with:
          server: ${{ secrets.FTP_SERVER }} # FTP server name (e.g., ftp.joelmuhoho.com)
          username: ${{ secrets.FTP_USERNAME }} # FTP username (e.g., joel@develop.lineage.joelmuhoho.com)
          password: ${{ secrets.FTP_PASSWORD }} # FTP password
          local-dir: ./ # local directory to deploy from
          server-dir: /${{secrets.DEVELOP_DIRECTORY_NAME }}/ # server directory to deploy to
          exclude: | # list of files/directories to exclude from deployment
            **/__pycache__/** # excludes all __pycache__ directories
            **/*.pyc # excludes all .pyc files
            .venv/** # excludes the virtual environment directory
            **/tests/** # excludes the tests directory  

```

Add the following secrets to your GitHub repository (**Settings > Secrets and variables > Actions**):

- `FTP_SERVER`: `ftp.joelmuhoho.com`
- `FTP_USERNAME`: `joel@develop.lineage.joelmuhoho.com`
- `FTP_PASSWORD`: Your newly created FTP password.
- `DIRECTORY_TO_DEPLOY_TO`: `/` *(Since the FTP account's root directory is already set to the application folder, we just deploy to `/`)*.

The GitHub Action workflow will sync the codebase to the FTP server and touch the `tmp/restart.txt` file, which signals Passenger to restart the Python application.

## 4. Application Configuration (`passenger_wsgi.py`)

When Passenger restarts, it loads `passenger_wsgi.py`. We have customized this file to automatically handle dependency installation and database migrations.

### Auto-Installing Dependencies
If `requirements.txt` changes, the application automatically installs them using the virtual environment's Python executable (`sys.executable`):

```python
import os, sys, subprocess

# Determine the absolute path of the application directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))
REQ_FILE = os.path.join(APP_DIR, "requirements.txt")

# Update requirements automatically
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQ_FILE])
except Exception as e:
    sys.stderr.write(f"Failed to install requirements: {e}\n")
```

### Auto-Running Migrations
Database migrations run automatically using Flask-Migrate before the app starts handling requests:

```python
from flask_migrate import upgrade
from app import create_app
from config import ProductionConfig

application = create_app(config_class=ProductionConfig)

# Run Database Migrations
with application.app_context():
    try:
        upgrade() # Runs equivalent of 'flask db upgrade'
    except Exception as e:
        application.logger.error(f"Failed to run automatic DB migrations: {e}")
```