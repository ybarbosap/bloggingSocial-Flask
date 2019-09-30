from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import data_required

class NameForm(FlaskForm):

    name = StringField('name', validators=[data_required()])
    submit = SubmitField('submit')