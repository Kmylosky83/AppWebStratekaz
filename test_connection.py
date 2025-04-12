import os
import sys
import logging
from dotenv import load_dotenv
import pymysql
from flask import Flask
from app import create_app
from app.extensions import db

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_mysql_connection():
    """Prueba la conexión directa a MySQL"""
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Configuración
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USERNAME', 'Kmylosky'),
            'password': os.getenv('DB_PASSWORD', 'Airetupal99*'),
            'database': os.getenv('DB_NAME', 'stratekaz')
        }
        
        logger.info("=== Iniciando prueba de conexión MySQL ===")
        logger.info(f"Host: {config['host']}")
        logger.info(f"Usuario: {config['user']}")
        logger.info(f"Base de datos: {config['database']}")
        
        # Probar conexión directa con PyMySQL
        logger.info("Probando conexión directa con PyMySQL...")
        connection = pymysql.connect(**config)
        
        with connection.cursor() as cursor:
            cursor.execute('SELECT VERSION()')
            version = cursor.fetchone()
            logger.info(f"✅ Versión de MySQL: {version[0]}")
            
            cursor.execute('SHOW TABLES')
            tables = cursor.fetchall()
            logger.info(f"Tablas existentes: {[table[0] for table in tables]}")
        
        connection.close()
        logger.info("✅ Prueba de conexión PyMySQL exitosa")
        
        # Probar conexión con Flask-SQLAlchemy
        logger.info("\n=== Probando conexión con Flask-SQLAlchemy ===")
        app = create_app()
        
        with app.app_context():
            # Mostrar URI de conexión (ocultando contraseña)
            uri = app.config['SQLALCHEMY_DATABASE_URI']
            safe_uri = uri.replace(config['password'], '****')
            logger.info(f"URI de conexión: {safe_uri}")
            
            # Probar conexión SQLAlchemy
            result = db.session.execute('SELECT 1').scalar()
            logger.info(f"✅ Prueba SQLAlchemy exitosa: {result}")
            
            # Listar tablas
            tables = db.session.execute('SHOW TABLES').fetchall()
            logger.info(f"Tablas desde SQLAlchemy: {[table[0] for table in tables]}")
        
        logger.info("✅ Todas las pruebas completadas exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante las pruebas: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == '__main__':
    test_mysql_connection()