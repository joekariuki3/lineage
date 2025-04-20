from app.models.user import User
from app.extensions import db

class AuthService:
    @staticmethod
    def authenticate(email, password):
        user = db.session.query(User).filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def register(name, email, password):
        """Register a new user."""
        if db.session.query(User).filter_by(email=email).first():
            return (400, ['Email already registered', 'danger'])

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return (201, ['Registration successful! Please log in.', 'success'])