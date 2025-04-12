import os
import logging
from flask_login import LoginManager
from app.extensions import db, login_manager
from dotenv import load_dotenv
import pymysql

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def init_db(app):
    """Inicializar y configurar la base de datos"""
    try:
        # Obtener y mostrar la configuración
        db_config = {
            'user': os.getenv('DB_USERNAME', 'Kmylosky'),
            'password': os.getenv('DB_PASSWORD', 'Airetupal99*'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'stratekaz')
        }
        
        logger.info(f"Configuración de base de datos:")
        logger.info(f"Host: {db_config['host']}")
        logger.info(f"Usuario: {db_config['user']}")
        logger.info(f"Base de datos: {db_config['database']}")
        
        # Configurar la URI de MySQL
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ECHO'] = True  # Para ver las consultas SQL
        
        logger.info("Probando conexión directa con PyMySQL...")
        connection = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        connection.close()
        logger.info("✅ Prueba de conexión exitosa")
        
        # Inicializar SQLAlchemy
        logger.info("Inicializando SQLAlchemy...")
        db.init_app(app)
        
        with app.app_context():
            # Crear tablas
            db.create_all()
            logger.info("✅ Tablas creadas correctamente")
            
            # Verificar la conexión
            result = db.session.execute('SELECT 1').scalar()
            logger.info(f"✅ Verificación de conexión: {result}")
        
        # Configurar login manager
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        logger.info("✅ Login manager configurado")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en init_db: {str(e)}")
        raise