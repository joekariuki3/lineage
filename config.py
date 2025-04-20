import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # General Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'jewl;asa445siweijkdsuei544554e689()')
    FLASK_APP = os.getenv('FLASK_APP', 'run.py')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('LINEAGE_DATABASE_URI', 'sqlite:///lineage.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Login
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE_CATEGORY = 'danger'

    # Flask-Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', '1') == '1'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    ADMINS = os.getenv('ADMINS', 'admin@example.com').split(',')

    # Guest User
    GUEST_NAME = os.getenv('GUEST_NAME')
    GUEST_EMAIL = os.getenv('GUEST_EMAIL')
    GUEST_PASSWORD = os.getenv('GUEST_PASSWORD')

    SALT = os.getenv('SALT')
    SECRET_KEY = os.getenv('SECRET_KEY')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log SQL queries

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "ewek;5584&^2dsjkdfskj5689dsjkn"

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

# Config selector
config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}