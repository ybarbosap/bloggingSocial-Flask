from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import Role
from flask_pagedown.fields import PageDownField

class NameForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    submit = SubmitField('submit')


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), 
                        Email(), 
                        Length(1, 64)])
    username = StringField('Username', validators=[
                           DataRequired(), 
                           Length(1, 64), 
                           Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                           'Usernames must have only letters, numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real Name', validators=[Length(1, 64)])
    location = StringField('Location', validators=[Length(1, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    #Contruct
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        # SelectField implements a drop dow list. A instance of SelectField must have your items identified 
        #... by a list of tuples.    
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user


    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email = field.data).first():
            raise ValidationError('Email already registered.')


    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username = field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(FlaskForm):
    body = PageDownField('What is on your mind?', validators=[DataRequired()])
    submit = SubmitField('Submit')
        

class DeletePost(FlaskForm):
    confirm = BooleanField('Confirm')
    submit = SubmitField('Delet')


class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    btn = SubmitField('Submit')