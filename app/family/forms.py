
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from wtforms.validators import DataRequired
from app.utils.constants import FamilyConstants

class CreateFamilyForm(FlaskForm):
    """form to create a family"""
    name = StringField('Family Name', validators=[DataRequired(message=FamilyConstants.FamilyRequired)], render_kw={"placeholder": FamilyConstants.FamilyPlaceholder})
    submit = SubmitField('Add')
