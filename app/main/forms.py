from flask_wtf import FlaskForm
from wtforms import (
    StringField, SubmitField, TextAreaField
)
from wtforms.validators import (
    data_required, Length
)

class NameForm(FlaskForm):

    name = StringField('name', validators=[data_required()])
    submit = SubmitField('submit')

class EditProfileForm(FlaskForm):
    
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')