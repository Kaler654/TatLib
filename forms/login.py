from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("пароль", validators=[DataRequired()])
    remember_me = BooleanField("запомнить меня")
    submit = SubmitField("войти")
