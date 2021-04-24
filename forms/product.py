from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired


class ProductsForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    price = IntegerField("Цена", validators=[DataRequired()])
    image = FileField("Фотография", validators=[DataRequired()])
    submit = SubmitField('Добавить')