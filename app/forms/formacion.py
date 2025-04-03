from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectMultipleField, FieldList, FormField
from wtforms.validators import DataRequired, Optional

class ObjetivoForm(FlaskForm):
    texto = StringField('Objetivo', validators=[DataRequired()])

class RecursoForm(FlaskForm):
    categoria = StringField('Categoría')
    recursos = FieldList(StringField('Recurso'), min_entries=1)

class FichaFormacionForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    fecha = DateTimeField('Fecha', validators=[DataRequired()])
    lugar = StringField('Lugar')
    duracion = StringField('Duración')
    responsable = StringField('Responsable', validators=[DataRequired()])
    
    # Metodologías
    metodologias = SelectMultipleField('Metodologías', choices=[
        ('clase_magistral', 'Clase Magistral'),
        ('exposicion_virtual', 'Exposición Virtual'),
        # Agregar más metodologías
    ])
    
    # Objetivos dinámicos
    objetivos = FieldList(FormField(ObjetivoForm), min_entries=1)
    
    # Recursos
    recursos = FieldList(FormField(RecursoForm), min_entries=1)