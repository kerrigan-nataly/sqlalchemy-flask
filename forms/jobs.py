from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, DateField
from wtforms.validators import DataRequired


class AddJobForm(FlaskForm):
    job = StringField('Работа', validators=[DataRequired()])
    work_size = IntegerField('Длительность', validators=[DataRequired()])
    team_leader = IntegerField('Руководитель', validators=[DataRequired()])
    start_date = DateField('Дата начала')
    collaborators = StringField('Работники')
    end_date = DateField('Дата окончания')
    is_finished = BooleanField('Завершена')
    submit = SubmitField('Добавить')
