from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import (
    DataRequired, Length, Email, Regexp, EqualTo
) 
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[ DataRequired(), Length(1, 64), Email() ])
    password = PasswordField('Password', validators=[DataRequired()])
    rememberMe = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
        'Usernames must have only letters, numbers, dots or undescores')
        # caso ocorra alguma falha na validação da expressão 
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Password must math')
        # EqualTo => Recebe um outro campo para compar e uma mensagem caso True 
    ])
    password2 = PasswordField('Confirm password', validators=[
        DataRequired()
    ])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    # Quando um método é chamado com o prefixo valide_ seguide do nome de 
    # um campo, o método é chamado como qualquer outro validador 
    # incluso em validators=[]