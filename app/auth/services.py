from app.models.user import User
from app.extensions import db
from config import Config
from app.user.services import create_user, save_user, get_user
from typing import Union, Tuple
from flask_login import login_user, logout_user, current_user

class AuthService:
    @staticmethod
    def authenticate(email: str, password: str) -> Union[User, Tuple[int, str, str]]:
        """Authenticate a user."""
        user = get_user(email=email)
        if user and user.check_password(password):
            login_user(user)
            return user
        return 403, 'Invalid username or password', 'danger'


    @staticmethod
    def register(name, email, password):
        """Register a new user."""
        if db.session.query(User).filter_by(email=email).first():
            return (400, ['Email already registered', 'danger'])

        user = create_user(name=name, email=email, password=password)
        if not user:
            return (500, ['Error creating user', 'danger'])
        status, message = save_user(user)
        if status != 201:
            return (status, message)
        return (201, ['Registration successful! Please log in.', 'success'])

    @staticmethod
    def get_guest_info():
        """Get guest user information."""
        return Config.GUEST_NAME,Config.GUEST_EMAIL,Config.GUEST_PASSWORD