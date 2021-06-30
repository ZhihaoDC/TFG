from wtforms import Form, TextField, BooleanField, FileField, RadioField, validators, widgets
from wtforms.fields.simple import SubmitField, StringField
from wtforms.validators import InputRequired, Required 
from flask_wtf import FlaskForm
from required import FieldsRequiredForm

class fileUploadForm(FieldsRequiredForm):
    file = FileField('fileUpload', validators=[InputRequired()])
    method = RadioField('Selecciona un método: ',
                        choices=[('GirvanNewman','Girvan-Newman'), ('Louvain','Louvain')])
    submit = SubmitField('Aplicar método')
