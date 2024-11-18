from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField,DateField, RadioField, validators, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from wtforms.fields import DateTimeLocalField
from models import User
from constants import NameConstants, EmailConstants, PasswordConstants, FamilyConstants, MemberConstants, GenderConstants, RelationshipConstants, EventConstants
class RegisterForm(FlaskForm):
    """form for a user to create an account"""
    name = StringField('Name', validators=[DataRequired(message=NameConstants.NameRequired)], render_kw={"placeholder": NameConstants.NamePlaceholder})
    email = EmailField('Email', validators=[DataRequired(message=EmailConstants.EmailRequired), Email(message=EmailConstants.EmailInvalid)], render_kw={"placeholder": EmailConstants.EmailPlaceholder})
    password = PasswordField('Password', validators=[DataRequired(message=PasswordConstants.PasswordRequired)], render_kw={"placeholder": PasswordConstants.PasswordPlaceholder})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(message=PasswordConstants.ConfirmPasswordRequired), EqualTo('password', message=PasswordConstants.PasswordMatch)], render_kw={"placeholder": PasswordConstants.ConfirmPasswordPlaceholder})
    submit = SubmitField('Register')

    def validate_email(self, email):
        """method to check if a user with passed email exists
        if yes prompt a user to choose a different email"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
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
    password2 = PasswordField('Repeat Password', validators=[DataRequired(message=PasswordConstants.ConfirmPasswordRequired), EqualTo('password', message=PasswordConstants.PasswordMatch)], render_kw={"placeholder": PasswordConstants.ConfirmPasswordPlaceholder})
    submit = SubmitField('Save New password')

class EditProfileForm(FlaskForm):
    """form to update details of a user"""
    name = StringField('Name', validators=[DataRequired(message=NameConstants.NameRequired)], render_kw={"placeholder": NameConstants.NamePlaceholder})
    email = EmailField('Email', validators=[DataRequired(message=EmailConstants.EmailRequired), Email(message=EmailConstants.EmailInvalid)], render_kw={"placeholder": EmailConstants.EmailPlaceholder})
    submit = SubmitField('Update')

class CreateFamilyForm(FlaskForm):
    """form to create a family"""
    name = StringField('Family Name', validators=[DataRequired(message=FamilyConstants.FamilyRequired)], render_kw={"placeholder": FamilyConstants.FamilyPlaceholder})
    submit = SubmitField('Add')

class MemberForm(FlaskForm):
    """form to add a family member"""
    first_name = StringField('First Name', validators=[DataRequired(message=MemberConstants.FirstNameRequired)], render_kw={"placeholder": MemberConstants.FirstNamePlaceholder})
    last_name = StringField('Last Name', validators=[DataRequired(message=MemberConstants.LastNameRequired)], render_kw={"placeholder": MemberConstants.LastNamePlaceholder})
    gender = SelectField('Gender', choices=[(gender, gender) for gender in GenderConstants.ALL], validators=[DataRequired(message=GenderConstants.GenderRequired)], render_kw={"placeholder":GenderConstants.GenderPlaceholder})
    birthdate = DateField('Birth Date', validators=[DataRequired(message=MemberConstants.BirthDateRequired)], render_kw={"placeholder": MemberConstants.BirthDatePlaceholder})
    alive = RadioField('Alive', choices=[(True, 'Yes'), (False, 'No')], validators=[DataRequired(message=MemberConstants.AliveRequired)])
    deathdate = DateField('Death Date', validators=(validators.Optional(),))
    relationship = SelectField('Relationship', choices=[], validators=[validators.Optional()])
    submit = SubmitField('Add')

    def __init__(self, add_relative_mode=None, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)

        # if add_relative_mode is True means add child or spouse add relationship field.
        if add_relative_mode:
            # Add appropriate choices based on the mode (Spouse or Child)
            self.relationship.validators=[DataRequired(message=RelationshipConstants.RelationshipRequired)]
            if add_relative_mode == RelationshipConstants.Spouse:
                self.relationship.choices = [(RelationshipConstants.Spouse, RelationshipConstants.Spouse)]
            elif add_relative_mode == RelationshipConstants.Child:
                self.relationship.choices = [(RelationshipConstants.Child, RelationshipConstants.Child)]

class AddEventForm(FlaskForm):
    """ form to add a new event of a family"""
    date = DateTimeLocalField('Event Date', validators=[DataRequired(message=EventConstants.DateRequired)], render_kw={"placeholder": EventConstants.DatePlaceholder})
    # date = DateField('')
    name = StringField('Event Name', validators=[DataRequired(message=EventConstants.NameRequired)], render_kw={"placeholder": EventConstants.NamePlaceholder})
    location = StringField('Venue', validators=[DataRequired(message=EventConstants.LocationRequired)], render_kw={"placeholder": EventConstants.LocationPlaceholder})
    description = TextAreaField('Event Description', validators=[DataRequired(message=EventConstants.DescriptionRequired)], render_kw={"placeholder": EventConstants.DescriptionPlaceholder})
    submit = SubmitField('Add Event')