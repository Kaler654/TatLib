from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SelectField


class TextForm(FlaskForm):
    author = StringField('Имя автора')
    title = StringField('Название книги/текста')
    file = FileField('книга/текст в формате .epab')
    difficult = SelectField('сложность', choices=[('1', "Новичок"), ('2', "Средний"), ('3', "Профи")])
    submit = SubmitField('готово')
