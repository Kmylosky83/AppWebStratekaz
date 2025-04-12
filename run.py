import os
import sys
import logging
from app import create_app
from app.extensions import db, socketio

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_app():
    try:
        # Usar la configuración que ya sabemos que funciona
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'
        
        app = create_app()
        return app
        
    except Exception as e:
        logger.error(f"Error al inicializar la aplicación: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        app = initialize_app()
        socketio.run(app, debug=True)
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}")
        sys.exit(1)