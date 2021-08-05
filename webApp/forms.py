from wtforms import Form, TextField, BooleanField, FileField, RadioField, validators, widgets
from wtforms.fields.simple import SubmitField, StringField
from wtforms.validators import InputRequired, Required, ValidationError 
from flask_wtf import FlaskForm
from required import FieldsRequiredForm
import pandas as pd

ALLOWED_EXTENSIONS = {'csv'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_csv(form, file):
    #File has .csv extension
    if not allowed_file(form.file.data.filename) :
        raise ValidationError("El tipo de archivo debe ser .csv")

# def is_edgelist(form, file):
#     file_path = './static/uploads' + '/' + form.file.data.filename
#     form.file.data.save(file_path)
#     df = pd.read_csv(file_path)

#     #File is an edgelist
#     print(df.shape)
#     if df.shape[1] != 2:
#         raise ValidationError("El contenido del .csv debe ser una lista de aristas (nodo1, nodo2)")
    

class fileUploadForm(FieldsRequiredForm):
    file = FileField('fileUpload', validators=[InputRequired(), is_csv])
    method = RadioField('Selecciona un método: ',
                        choices=[('GirvanNewman','Girvan-Newman'), ('Louvain','Louvain')])
    submit = SubmitField('Aplicar método')

