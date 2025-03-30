from app import create_app, db
from app.models.user import User
from app.models.empresa import Empresa
from app.models.tarea import Tarea
from app.models.formacion import FichaFormacion, ListaAsistencia, Asistente, PreguntaFormacion, RespuestaFormacion

app = create_app()

with app.app_context():
    # Crear todas las tablas
    db.create_all()
    print("Base de datos inicializada correctamente.")