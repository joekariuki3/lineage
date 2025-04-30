from app.models.user import User
from app.extensions import db
from config import Config
from app.user.services import create_user, save_user, get_user
from typing import Union, Tuple, Optional
from flask_login import login_user, logout_user, current_user

class AuthService:
    @staticmethod
    def authenticate(email: str, password: str) -> Union[User, Tuple[int, str, str]]:
        """Authenticate a user."""
        user = get_user(email=email)
        if user and user.check_password(password):
            login_user(user)

            AuthService.set_current_family_id()
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

    @staticmethod
    def set_current_family_id(current_family_id: Optional[int] = None) -> None:
        """Set the current family ID for the current user."""
        if current_user.is_authenticated:
            families_length = len(current_user.families)
            if families_length == 1:
                setattr(current_user, 'current_family_id', current_user.families[0].family_id)
            elif families_length > 1 and current_family_id:
                setattr(current_user, 'current_family_id', current_family_id)
