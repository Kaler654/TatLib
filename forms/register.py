from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('имя', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('пароль', validators=[DataRequired()])
    password_again = PasswordField('повторите пароль', validators=[DataRequired()])
    submit = SubmitField('готово')