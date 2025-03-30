from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def init_db(app):
    try:
        # Determinar si estamos en entorno local
        is_local = os.getenv('FLASK_ENV') == 'development' or os.path.exists('C:/Proyectos')
        
        if is_local:
            # Usar SQLite para desarrollo local
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
            print("Ambiente local detectado: usando SQLite")
        else:
            # Configuración de producción para el hosting
            username = os.getenv('DB_USERNAME')
            password = os.getenv('DB_PASSWORD')
            host = os.getenv('DB_HOST')
            database = os.getenv('DB_NAME')
            app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}/{database}'
            
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Inicializar extensiones
        db.init_app(app)
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        
        return True
    except Exception as e:
        print(f"Error inicializando la base de datos: {str(e)}")
        return False