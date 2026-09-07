
from flask import session
from flask_login import current_user, login_user

from app.models.user import User
from app.services.service_base import service_response
from app.user.services import UserService
from config import Config


class AuthService:

    @staticmethod
    def authenticate(email: str, password: str) -> User | tuple[dict, int]:
        user_service = UserService()

        data, _ = user_service.get_user(email=email)
        user = data.get('data')
        if user and user.check_password(password):
            login_user(user)
            AuthService.set_current_family_id()
            return service_response(200, 'Login successful', 'success', user)
        return service_response(403, 'Invalid username or password', 'danger', None)

    @staticmethod
    def get_guest_info()-> tuple[str, str, str]:
        """Get guest user information."""
        return Config.GUEST_NAME,Config.GUEST_EMAIL,Config.GUEST_PASSWORD

    @staticmethod
    def set_current_family_id(current_family_id: int | None = None):
        """Set the current family ID for the current user."""
        if current_user and current_user.is_authenticated:
            families_length = len(current_user.families)
            if families_length == 1:
                session['current_family_id'] = current_user.families[0].family_id
            elif families_length > 1 and current_family_id:
                session['current_family_id'] = current_family_id
            return session
        return None