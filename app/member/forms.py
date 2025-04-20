from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, RadioField, validators
from wtforms.validators import DataRequired
from app.utils.constants import MemberConstants, GenderConstants, RelationshipConstants

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
        """
        Initializes the MemberForm with optional settings for adding a relative.

        Parameters:
        add_relative_mode (str): Determines the relationship mode for the form.
            If set, configures the relationship field with appropriate validators
            and choices for adding a spouse or child.

        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

        The relationship field is only configured if add_relative_mode is provided.
        """
        super(MemberForm, self).__init__(*args, **kwargs)

        # if add_relative_mode is True means add child or spouse add relationship field.
        if add_relative_mode:
            # Add appropriate choices based on the mode (Spouse or Child)
            self.relationship.validators=[DataRequired(message=RelationshipConstants.RelationshipRequired)]
            if add_relative_mode == RelationshipConstants.Spouse:
                self.relationship.choices = [(RelationshipConstants.Spouse, RelationshipConstants.Spouse)]
            elif add_relative_mode == RelationshipConstants.Child:
                self.relationship.choices = [(RelationshipConstants.Child, RelationshipConstants.Child)]
