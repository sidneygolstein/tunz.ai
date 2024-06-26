from flask_wtf import FlaskForm
from wtforms import Form, FieldList, FormField, RadioField, TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired

class RatingForm(Form):
    rating = RadioField('Rating', choices=[(str(i), str(i)) for i in range(1, 6)], validators=[DataRequired()])

class ReviewForm(FlaskForm):
    questions = FieldList(FormField(RatingForm), min_entries=0)
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit')