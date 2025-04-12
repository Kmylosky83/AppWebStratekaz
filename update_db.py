from app import create_app
from app.extensions import db
from flask_migrate import upgrade

def init_db():
    app = create_app()
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            print("Base de datos inicializada correctamente")
            
            # Aplicar migraciones pendientes
            upgrade()
            print("Migraciones aplicadas correctamente")
            
            return True
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")
            return False

if __name__ == '__main__':
    init_db()
