from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField,DateField, RadioField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from models import User
from flask_login import current_user

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

class CreateFamilyForm(FlaskForm):
    name = StringField('Family Name', validators=[DataRequired()])
    submit = SubmitField('Add')

class AddMemberForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Male', 'Female'), ('Male', 'Others') ], validators=[DataRequired()])
    birthdate = DateField('Birth Date')
    alive = RadioField('Alive', choices=[('Yes'), ('No')], validators=[DataRequired()])
    deathdate = DateField('Death Date')
    submit = SubmitField('Add')

class AddMemberSpouseForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Male', 'Female'), ('Male', 'Others') ], validators=[DataRequired()])
    birthdate = DateField('Birth Date')
    alive = RadioField('Alive', choices=[('Yes'), ('No')], validators=[DataRequired()])
    deathdate = DateField('Death Date')
    relationship = SelectField('Relationship', choices=[('spouse')], validators=[DataRequired()])
    submit = SubmitField('Add')
class AddMemberChildForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Male', 'Female'), ('Male', 'Others') ], validators=[DataRequired()])
    birthdate = DateField('Birth Date')
    alive = RadioField('Alive', choices=[('Yes'), ('No')], validators=[DataRequired()])
    deathdate = DateField('Death Date')
    relationship = SelectField('Relationship', choices=[('child')], validators=[DataRequired()])
    submit = SubmitField('Add')

