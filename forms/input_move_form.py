from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class MoveForm(FlaskForm):
    move = StringField('', validators=[DataRequired()])
    submit = SubmitField('Походить')