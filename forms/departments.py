from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, EmailField
from wtforms.validators import DataRequired, Email


class AddDepartmentForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    chief_id = IntegerField('Ответственный', validators=[DataRequired()])
    members = StringField('Сотрудники')
    email = EmailField('Электронная почта', validators=[DataRequired(), Email()])
    submit = SubmitField('Добавить')


class EditDepartmentForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    chief_id = IntegerField('Ответственный', validators=[DataRequired()])
    members = StringField('Сотрудники')
    email = EmailField('Электронная почта', validators=[DataRequired(), Email()])
    submit = SubmitField('Сохранить')
