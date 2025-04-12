import pymysql
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_database():
    try:
        # Conectar sin especificar base de datos
        connection = pymysql.connect(
            host='localhost',
            user='Kmylosky',
            password='Airetupal99*'
        )
        
        logger.info("✅ Conexión exitosa a MySQL")
        
        with connection.cursor() as cursor:
            # Crear la base de datos si no existe
            cursor.execute("CREATE DATABASE IF NOT EXISTS stratekaz CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info("✅ Base de datos 'stratekaz' creada correctamente")
            
            # Verificar que la base de datos existe
            cursor.execute("SHOW DATABASES LIKE 'stratekaz'")
            if cursor.fetchone():
                logger.info("✅ Verificación: la base de datos existe")
            
        connection.close()
        logger.info("✅ Proceso completado exitosamente")
        return True
        
    except pymysql.Error as e:
        logger.error(f"❌ Error de MySQL: {e.args[0]} - {e.args[1]}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        return False

if __name__ == '__main__':
    create_database()