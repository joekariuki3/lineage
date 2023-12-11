from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField,DateField, RadioField, validators, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from wtforms.fields import DateTimeLocalField
from models import User
from flask_login import current_user

class RegisterForm(FlaskForm):
    """form for a user to create an account"""
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        """method to check if a user with passed email exists
        if yes prompt a user to choose a different email"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    """form for a user to login"""
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class EditProfileForm(FlaskForm):
    """form to update details of a user"""
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

class CreateFamilyForm(FlaskForm):
    """form to create a family"""
    name = StringField('Family Name', validators=[DataRequired()])
    submit = SubmitField('Add')

class AddMemberForm(FlaskForm):
    """form to add a family member"""
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others') ], validators=[DataRequired()])
    birthdate = DateField('Birth Date')
    alive = RadioField('Alive', choices=[(True, 'Yes'), (False, 'No')], validators=[DataRequired()])
    deathdate = DateField('Death Date', validators=(validators.Optional(),))
    submit = SubmitField('Add')

class AddMemberSpouseForm(FlaskForm):
    """form to add a spouse"""
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others') ], validators=[DataRequired()])
    birthdate = DateField('Birth Date')
    alive = RadioField('Alive', choices=[(True, 'Yes'), (False, 'No')], validators=[DataRequired()])
    deathdate = DateField('Death Date', validators=(validators.Optional(),))
    relationship = SelectField('Relationship', choices=[('spouse')], validators=[DataRequired()])
    submit = SubmitField('Add')

class AddMemberChildForm(FlaskForm):
    """form to add a child"""
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others') ], validators=[DataRequired()])
    birthdate = DateField('Birth Date')
    alive = RadioField('Alive', choices=[(True, 'Yes'), (False, 'No')], validators=[DataRequired()])
    deathdate = DateField('Death Date', validators=(validators.Optional(),))
    relationship = SelectField('Relationship', choices=[('child')], validators=[DataRequired()])
    submit = SubmitField('Add')

class updateMemberForm(FlaskForm):
    """form to update details of a member"""
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others') ], validators=[DataRequired()])
    birthdate = DateField('Birth Date')
    alive = RadioField('Alive', choices=[(True, 'Yes'), (False, 'No')], validators=[DataRequired()])
    deathdate = DateField('Death Date', validators=(validators.Optional(),))
    submit = SubmitField('Update')

class AddEventForm(FlaskForm):
    """ form to add a new event of a family"""
    date = DateTimeLocalField('Event Date', validators=[DataRequired()])
    # date = DateField('')
    name = StringField('Event Name', validators=[DataRequired()])
    location = StringField('Venue', validators=[DataRequired()])
    description = TextAreaField('Event Description', validators=[DataRequired()])
    submit = SubmitField('Add Event')