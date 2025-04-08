from flask import Flask, render_template
from datetime import datetime, timedelta
from app.config.config import config
from app.config.database import init_db, db, login_manager
from flask_migrate import Migrate
from flask_socketio import SocketIO
import os

# Inicializar SocketIO antes de crear la app
socketio = SocketIO()

def create_app():
    # Inicializar la aplicación Flask
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config['development'])
    
    # Configurar carpeta de uploads
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicializar base de datos
    init_db(app)
    
    # Inicializar Migrate
    migrate = Migrate(app, db)
    
    # Inicializar SocketIO con la app
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Registrar blueprints
    from app.controllers.auth.routes import auth_bp
    from app.controllers.dashboard.routes import dashboard_bp
    from app.controllers.empresas.routes import empresas_bp
    from app.controllers.main.routes import main_bp
    from app.controllers.tareas.routes import tareas_bp
    from app.controllers.formacion.routes import formacion_bp
    from app.controllers.kmy.routes import kmy_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(empresas_bp, url_prefix='/empresas')
    app.register_blueprint(main_bp)
    app.register_blueprint(tareas_bp, url_prefix='/tareas')
    app.register_blueprint(formacion_bp, url_prefix='/formacion')
    app.register_blueprint(kmy_bp, url_prefix='/api/kmy')
    
    # Configurar login_manager
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    login_manager.remember_cookie_duration = timedelta(days=30)
    
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
        
    @app.template_filter('from_json')
    def parse_json(value):
        import json
        try:
            return json.loads(value)
        except:
            return []
        
    return app

# Importar los modelos
from app.models.user import User
from app.models.empresa import Empresa
from app.models.tarea import Tarea     
from app.models.formacion import FichaFormacion, ListaAsistencia, Asistente, PreguntaFormacion, RespuestaFormacion

# Crea la aplicación
app = create_app()