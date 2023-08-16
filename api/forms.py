from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_security.forms import LoginForm, RegisterForm, Form


class logform(LoginForm):
    login = StringField('login', validators=[DataRequired()])
    # password = PasswordField('password', validators=[DataRequired()])


class signupform(RegisterForm):
    # email = StringField('email', validators=[Email(), DataRequired()])
    username = StringField('username', [DataRequired()])
    # password = PasswordField('password', validators=[DataRequired()])