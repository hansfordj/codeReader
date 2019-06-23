from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField, SelectField, validators, ValidationError
from flask_wtf import Form
from wtforms.fields.html5 import DateField

class PostForm(FlaskForm):
    post = TextAreaField('Create Post', [validators.DataRequired(), validators.Length(min=1, max=140)])
    submit = SubmitField('Submit')

