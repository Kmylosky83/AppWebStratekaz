import pymysql
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_mysql_connection():
    try:
        # Credenciales explícitas
        config = {
            'host': 'localhost',
            'user': 'Kmylosky',
            'password': 'Airetupal99*',
            'database': 'stratekaz'
        }
        
        logger.info("Configuración de conexión:")
        logger.info(f"Host: {config['host']}")
        logger.info(f"Usuario: {config['user']}")
        logger.info(f"Base de datos: {config['database']}")
        
        logger.info(f"Intentando conectar a MySQL como {config['user']}@{config['host']}...")
        
        # Intentar conexión
        connection = pymysql.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            connect_timeout=5
        )
        
        logger.info("✅ Conexión exitosa a MySQL")
        
        # Probar crear una tabla de prueba
        with connection.cursor() as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id INT)")
            logger.info("✅ Tabla de prueba creada correctamente")
            
            # Eliminar la tabla de prueba
            cursor.execute("DROP TABLE test_table")
            logger.info("✅ Tabla de prueba eliminada correctamente")
        
        connection.close()
        logger.info("✅ Prueba completada exitosamente")
        return True
        
    except pymysql.Error as e:
        logger.error(f"❌ Error de MySQL: {e.args[0]} - {e.args[1]}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        return False

if __name__ == '__main__':
    test_mysql_connection()