from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,DateField, validators, TextAreaField
from wtforms.validators import DataRequired
from wtforms.fields import DateTimeLocalField
from constants import EventConstants


class AddEventForm(FlaskForm):
    """ form to add a new event of a family"""
    date = DateTimeLocalField('Event Date', validators=[DataRequired(message=EventConstants.DateRequired)], render_kw={"placeholder": EventConstants.DatePlaceholder})
    # date = DateField('')
    name = StringField('Event Name', validators=[DataRequired(message=EventConstants.NameRequired)], render_kw={"placeholder": EventConstants.NamePlaceholder})
    location = StringField('Venue', validators=[DataRequired(message=EventConstants.LocationRequired)], render_kw={"placeholder": EventConstants.LocationPlaceholder})
    description = TextAreaField('Event Description', validators=[DataRequired(message=EventConstants.DescriptionRequired)], render_kw={"placeholder": EventConstants.DescriptionPlaceholder})
    submit = SubmitField('Add Event')
