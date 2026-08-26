from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.user.services import UserService
from app.utils.constants import EmailConstants, NameConstants, PasswordConstants


class RegisterForm(FlaskForm):
    """form for a user to create an account"""
    def __init__(self):
        super().__init__()
        self.user_service = UserService()

    name = StringField('Name', validators=[DataRequired(message=NameConstants.NameRequired)], render_kw={"placeholder": NameConstants.NamePlaceholder})
    email = EmailField('Email', validators=[DataRequired(message=EmailConstants.EmailRequired), Email(message=EmailConstants.EmailInvalid)], render_kw={"placeholder": EmailConstants.EmailPlaceholder})
    password = PasswordField('Password', validators=[DataRequired(message=PasswordConstants.PasswordRequired)], render_kw={"placeholder": PasswordConstants.PasswordPlaceholder})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(message=PasswordConstants.ConfirmPasswordRequired), EqualTo('password', message=PasswordConstants.PasswordMatch)], render_kw={"placeholder": PasswordConstants.ConfirmPasswordPlaceholder})
    submit = SubmitField('Register')

    def validate_email(self, email):
        """method to check if a user with passed email exists
        if yes prompt a user to choose a different email"""
        if self.user_service.check_user_exists(email=email.data):
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    """form for a user to login"""
    email = EmailField('Email', validators=[DataRequired(message=EmailConstants.EmailRequired), Email(message=EmailConstants.EmailInvalid)], render_kw={"placeholder": EmailConstants.EmailPlaceholder})
    password = PasswordField('Password', validators=[DataRequired(message=PasswordConstants.PasswordRequired)], render_kw={"placeholder": PasswordConstants.PasswordPlaceholder})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ResetPasswordRequestForm(FlaskForm):
    """User resets password"""
    email = EmailField('Email', validators=[DataRequired(message=EmailConstants.EmailRequired), Email(message=EmailConstants.EmailInvalid)], render_kw={"placeholder": EmailConstants.EmailPlaceholder})
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(message=PasswordConstants.PasswordRequired)], render_kw={"placeholder": PasswordConstants.PasswordPlaceholder})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(message=PasswordConstants.ConfirmPasswordRequired), EqualTo('password', message=PasswordConstants.PasswordMatch)], render_kw={"placeholder": PasswordConstants.ConfirmPasswordPlaceholder})
    submit = SubmitField('Save New password')
