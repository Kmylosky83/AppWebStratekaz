import pymysql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_mysql_permissions():
    try:
        # Conectar como root primero para verificar/crear usuario
        connection = pymysql.connect(
            host='localhost',
            user='Kmylosky',
            password='Airetupal99*'
        )
        
        with connection.cursor() as cursor:
            # Ver si el usuario puede crear bases de datos
            cursor.execute("SHOW GRANTS FOR CURRENT_USER")
            grants = cursor.fetchall()
            logger.info("Permisos actuales:")
            for grant in grants:
                logger.info(grant[0])
            
            # Intentar crear la base de datos
            cursor.execute("CREATE DATABASE IF NOT EXISTS stratekaz")
            logger.info("Base de datos 'stratekaz' creada/verificada")
            
            # Asegurar que el usuario tiene todos los permisos necesarios
            cursor.execute(f"GRANT ALL PRIVILEGES ON stratekaz.* TO 'Kmylosky'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            logger.info("Permisos otorgados correctamente")
            
        connection.close()
        logger.info("✅ Verificación de permisos completada")
        return True
        
    except pymysql.Error as e:
        logger.error(f"❌ Error de MySQL: {e.args[0]} - {e.args[1]}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        return False

if __name__ == '__main__':
    check_mysql_permissions()