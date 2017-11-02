from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length

class PostsForm(FlaskForm):
    content = TextAreaField('', render_kw={'placeholder': '这一刻的想法...'},
                            validators=[DataRequired()])
    submit = SubmitField('发表')
    def validate_content(self,field):
        if len(field.data) < 1:
            raise ValidationError('亲，发表不能为空哦~~~')
        elif len(field.data) > 128:
            raise ValidationError('亲，字数太多了，少写点哈^-^')