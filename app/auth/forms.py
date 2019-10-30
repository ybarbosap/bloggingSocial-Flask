from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField, ValidationError, TextAreaField
)
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


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[
        DataRequired(), EqualTo('password2', message='Password must match.')
    ])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update password')


class ChangeEmail(FlaskForm):
    old_email = StringField('Old email', validators=[DataRequired()])
    new_email = StringField('New email', validators=[DataRequired(),
                            EqualTo('new_email2', message='Password must match.')])
    password = PasswordField('Password')
    submit = SubmitField('Update email.')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),
                        Length(1, 64), Email()])
    submit = SubmitField('Reset Password.')










    # Quando um método é chamado com o prefixo valide_ seguido do nome de 
    # um campo, o método é chamado como qualquer outro validador 
    # incluso em validators=[]