import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # General Config
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(16).hex())
    FLASK_APP = os.getenv("FLASK_APP", "run.py")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("LINEAGE_DATABASE_URI", "sqlite:///lineage.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Login
    LOGIN_VIEW = "auth.login"
    LOGIN_MESSAGE_CATEGORY = "danger"

    # Flask-Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "1") == "1"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    ADMINS = os.getenv("ADMINS", "admin@example.com").split(",")

    # Guest User
    GUEST_NAME = os.getenv("GUEST_NAME")
    GUEST_EMAIL = os.getenv("GUEST_EMAIL")
    GUEST_PASSWORD = os.getenv("GUEST_PASSWORD")

    SALT = os.getenv("SALT", os.urandom(16).hex())


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO")  # Log SQL queries


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test-db:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(16).hex())


class ProductionConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("LINEAGE_DATABASE_URI")
