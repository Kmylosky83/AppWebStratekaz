from flask import Flask, render_template
from datetime import datetime
from app.config.config import config
from app.config.database import init_db, db, login_manager

def create_app():
    # Inicializar la aplicación Flask
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config['development'])
    
    # Inicializar base de datos
    init_db(app)
    
    # Registrar blueprints
    from app.controllers.auth.routes import auth_bp
    from app.controllers.dashboard.routes import dashboard_bp
    from app.controllers.empresas.routes import empresas_bp
    from app.controllers.main.routes import main_bp
    from app.controllers.tareas.routes import tareas_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(empresas_bp, url_prefix='/empresas')
    app.register_blueprint(main_bp)
    app.register_blueprint(tareas_bp, url_prefix='/tareas')
    
    # Configurar login_manager
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
        
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    
    # Manejar errores
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
        
    # Configurar contexto global
    @app.context_processor
    def utility_processor():
        return dict(
            app_name='StrateKaz',
            current_year=datetime.now().year
        )
        
    return app

# Importar los modelos
from app.models.user import User
from app.models.empresa import Empresa
from app.models.tarea import Tarea        
        
