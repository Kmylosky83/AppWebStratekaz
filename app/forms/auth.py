from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SelectField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class RegistrationForm(FlaskForm):
    # Campos comunes
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message="Por favor ingrese un email válido")
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=8, message="La contraseña debe tener al menos 8 caracteres")
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    phone = StringField('Teléfono', validators=[
        DataRequired(),
        Length(min=10, max=10, message="El número debe tener 10 dígitos")
    ])
    city = StringField('Ciudad', validators=[DataRequired()])
    department = SelectField('Departamento', choices=[
        ('', 'Seleccione...'),
        ('Amazonas', 'Amazonas'),
        ('Antioquia', 'Antioquia'),
        ('Arauca', 'Arauca'),
        # ... Agregar todos los departamentos
    ])

    # Campos para profesional independiente
    first_name = StringField('Nombres')
    last_name = StringField('Apellidos')
    profession = StringField('Profesión')

    # Campos para empresa
    company_name = StringField('Nombre de la Empresa')
    nit = StringField('NIT')
    company_type = SelectField('Tipo de Empresa', choices=[
        ('', 'Seleccione...'),
        ('direct', 'Empresa Directa'),
        ('consultant', 'Consultora')
    ])
    industry = SelectField('Industria', choices=[
        ('', 'Seleccione...'),
        ('mining', 'Minería y Energía'),
        ('manufacturing', 'Industria Manufacturera'),
        # ... Agregar todas las industrias
    ])
    contact_position = StringField('Cargo')

    # Verificación
    recaptcha = RecaptchaField()

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Este email ya está registrado.')

    def validate_nit(self, field):
        if field.data and User.query.filter_by(nit=field.data).first():
            raise ValidationError('Este NIT ya está registrado.')