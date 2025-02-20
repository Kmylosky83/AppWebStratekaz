from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

def init_db(app):
    try:
        # Configurar la base de datos
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://appwebuser:AppWeb2024@localhost/appwebstratekaz'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Inicializar extensiones
        db.init_app(app)
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        
        return True
    except Exception as e:
        print(f"Error inicializando la base de datos: {str(e)}")
        return False