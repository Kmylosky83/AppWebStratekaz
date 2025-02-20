from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from app.config.database import db
from flask_login import LoginManager
from app.models.user import User  # Añadido

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = 'AppWebStratekaz2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://appwebuser:AppWeb2024@localhost/appwebstratekaz'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        # Importar y registrar blueprints
        from app.controllers.auth.routes import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        
        from app.controllers.dashboard.routes import dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
        
        from app.controllers.empresas.routes import empresas_bp
        app.register_blueprint(empresas_bp, url_prefix='/empresas')
        
        # Ruta raíz
        @app.route('/')
        def root():
            return redirect(url_for('auth.login'))
        
        # Crear todas las tablas
        db.create_all()
    
    return app