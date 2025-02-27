from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, validators
from wtforms.validators import DataRequired, Email
from constants import NameConstants, EmailConstants


class EditProfileForm(FlaskForm):
    """form to update details of a user"""
    name = StringField('Name', validators=[DataRequired(message=NameConstants.NameRequired)], render_kw={"placeholder": NameConstants.NamePlaceholder})
    email = EmailField('Email', validators=[DataRequired(message=EmailConstants.EmailRequired), Email(message=EmailConstants.EmailInvalid)], render_kw={"placeholder": EmailConstants.EmailPlaceholder})
    submit = SubmitField('Update')
