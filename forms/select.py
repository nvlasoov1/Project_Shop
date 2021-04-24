from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
import oxr

EXCHANGE_RATES = oxr.latest()
countries = EXCHANGE_RATES.keys()


class SelectForm(FlaskForm):
    cur = SelectField(u'Курс валюты', choices=[(country, country) for country in countries],
                      validators=[DataRequired()])
    submit = SubmitField('Подтвердить смену валюты')