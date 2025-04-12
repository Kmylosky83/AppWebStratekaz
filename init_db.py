from app import create_app
from app.extensions import db
from flask_migrate import upgrade
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_db():
    try:
        logger.info("Creando aplicación Flask...")
        app = create_app()
        
        with app.app_context():
            # Verificar la conexión a la base de datos
            logger.info(f"Conectando a: {app.config['SQLALCHEMY_DATABASE_URI']}")
            connection = db.engine.connect()
            logger.info("✅ Conexión exitosa a la base de datos")
            connection.close()
            
            # Crear todas las tablas
            logger.info("Creando tablas...")
            db.create_all()
            logger.info("✅ Tablas creadas correctamente")
            
            # Aplicar migraciones
            logger.info("Aplicando migraciones...")
            upgrade()
            logger.info("✅ Migraciones aplicadas correctamente")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error al inicializar la base de datos: {str(e)}")
        raise

if __name__ == '__main__':
    init_db()