from app import app
from app.config.database import db

def add_respuesta_correcta_column():
    with app.app_context():
        try:
            db.engine.execute('ALTER TABLE preguntas_formacion ADD COLUMN respuesta_correcta VARCHAR(200)')
            print("Columna respuesta_correcta agregada exitosamente")
        except Exception as e:
            print(f"Error al agregar columna: {str(e)}")

if __name__ == "__main__":
    add_respuesta_correcta_column()