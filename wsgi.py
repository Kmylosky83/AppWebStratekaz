import os
import logging
from app import create_app
from app.extensions import db, socketio

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app('development')

def init_database():
    """Initialize the database and create all tables"""
    with app.app_context():
        try:
            # Asegurar que el directorio instance existe y tiene permisos
            instance_path = os.path.join(os.path.dirname(__file__), 'instance')
            os.makedirs(instance_path, exist_ok=True)
            os.chmod(instance_path, 0o777)
            logger.info(f"Instance directory initialized at: {instance_path}")
            
            # Asegurar que el archivo de base de datos tiene permisos
            db_path = os.path.join(instance_path, 'app.db')
            if os.path.exists(db_path):
                os.chmod(db_path, 0o666)
            
            # Crear tablas
            db.create_all()
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return False

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    
    logger.info("Starting server...")
    socketio.run(app, debug=True)