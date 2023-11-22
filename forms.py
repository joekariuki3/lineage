from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, EmailField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from models import User

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm_Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')