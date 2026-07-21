#!/usr/bin/env python3
import os
import subprocess  # nosec B404
import sys
from app import create_app
from config import ProductionConfig
from flask_migrate import upgrade  # noqa: E402

# Determine the absolute path to your application directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))
REQ_FILE = os.path.join(APP_DIR, "requirements.txt")

# Update requirements
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQ_FILE])  # nosec B603
except Exception as e:
    sys.stderr.write(f"Failed to install requirements: {e}\n")


application = create_app(config_class=ProductionConfig)

# Run Database Migrations
with application.app_context():
    try:
        # runs 'flask db upgrade'
        upgrade()
    except Exception as e:
        application.logger.error(f"Failed to run automatic DB migrations: {e}")


if __name__ == "__main__":
    application.run()