import os
from datetime import datetime, timedelta
from flask import Flask, render_template
from app.extensions import db, login_manager, socketio, mail, migrate, cache, init_extensions
import logging
from pathlib import Path

def create_app(config_name=None):
    """Factory para crear y configurar la aplicación Flask"""
    try:
        # 1. Inicialización básica de la app
        app = Flask(__name__, instance_relative_config=True)
        
        # Determinar el entorno si no se especifica
        if config_name is None:
            config_name = 'development'
        
        # 2. Configuración de directorios e instancia
        configure_instance_folder(app)
        
        # 3. Cargar configuración
        load_configuration(app, config_name)
        
        # 4. Configuración de logging
        setup_logging(app)
        
        # 5. Inicializar extensiones (incluye base de datos)
        init_extensions(app)
        
        # 6. Configuraciones adicionales
        with app.app_context():
            configure_blueprints(app)
            configure_authentication(app)
            configure_upload_folders(app)
            register_error_handlers(app)
            configure_template_context(app)
        
        # 7. Verificación final
        app.logger.info(f"Aplicación inicializada en modo {config_name.upper()}")
        
        return app
        
    except Exception as e:
        print(f"❌ Error fatal al crear la aplicación: {str(e)}")
        raise

def configure_instance_folder(app):
    """Configurar y verificar el directorio instance"""
    try:
        instance_path = Path(app.instance_path)
        instance_path.mkdir(exist_ok=True, mode=0o755)  # Más seguro que 777
        
        # Verificar permisos
        if not os.access(instance_path, os.W_OK):
            app.logger.warning(f"ADVERTENCIA: Permisos insuficientes en {instance_path}")
    except Exception as e:
        app.logger.error(f"Error configurando directorio instance: {e}")
        raise

def load_configuration(app, config_name):
    """Cargar configuración según el entorno"""
    try:
        from app.config.config import config
        app.config.from_object(config[config_name])
        
        # Cargar configuración adicional desde archivo si existe
        instance_config = Path(app.instance_path) / 'config.py'
        if instance_config.exists():
            app.config.from_pyfile(instance_config)
            
    except Exception as e:
        app.logger.error(f"Error cargando configuración: {e}")
        raise

def setup_logging(app):
    """Configurar sistema de logging"""
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
        
        # En producción, registrar también a archivo
        if app.config.get('ENV') == 'production':
            logs_dir = Path(app.instance_path) / 'logs'
            logs_dir.mkdir(exist_ok=True)
            
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                logs_dir / 'app.log',
                maxBytes=1024 * 1024 * 5,  # 5MB
                backupCount=3
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            app.logger.addHandler(file_handler)

def configure_blueprints(app):
    """Registrar todos los blueprints"""
    from app.controllers.auth.routes import auth_bp
    from app.controllers.dashboard.routes import dashboard_bp
    from app.controllers.empresas.routes import empresas_bp
    from app.controllers.main.routes import main_bp
    from app.controllers.tareas.routes import tareas_bp
    from app.controllers.formacion.routes import formacion_bp
    from app.controllers.kmy.routes import kmy_bp
    
    blueprints = [
        (auth_bp, '/auth'),
        (dashboard_bp, '/dashboard'),
        (empresas_bp, '/empresas'),
        (main_bp, ''),
        (tareas_bp, '/tareas'),
        (formacion_bp, '/formacion'),
        (kmy_bp, '/api/kmy')
    ]
    
    for bp, url_prefix in blueprints:
        app.register_blueprint(bp, url_prefix=url_prefix)
    
    app.logger.info(f"Registrados {len(blueprints)} blueprints")

def configure_authentication(app):
    """Configurar autenticación y manejo de usuarios"""
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            app.logger.error(f"Error cargando usuario {user_id}: {e}")
            return None
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    login_manager.remember_cookie_duration = timedelta(days=30)
    login_manager.session_protection = "strong"
    
    # Inicializar roles y permisos
    try:
        from app.utils.role_utils import init_roles_and_permissions
        init_roles_and_permissions()
        app.logger.info("Roles y permisos inicializados")
    except Exception as e:
        app.logger.error(f"Error inicializando roles: {e}")

def initialize_database(app):
    """Inicializar y verificar la base de datos"""
    try:
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        app.logger.info(f"Intentando conectar a la base de datos: {db_uri}")
        
        # Crear todas las tablas
        with app.app_context():
            db.create_all()
            app.logger.info("✅ Base de datos inicializada correctamente")
            
            # Verificar la conexión
            db.session.execute('SELECT 1')
            app.logger.info("✅ Conexión a la base de datos verificada")
            
    except Exception as e:
        app.logger.error(f"❌ Error inicializando base de datos: {e}")
        # Re-raise para que el error sea visible
        raise

def configure_upload_folders(app):
    """Configurar carpetas para archivos subidos"""
    upload_folder = Path(app.static_folder) / 'uploads'
    upload_folder.mkdir(exist_ok=True, mode=0o755)
    
    app.config['UPLOAD_FOLDER'] = str(upload_folder)
    app.logger.info(f"Carpeta de uploads configurada en {upload_folder}")

def register_error_handlers(app):
    """Registrar manejadores de errores personalizados"""
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Error 500: {str(e)}")
        return render_template('errors/500.html'), 500

def configure_template_context(app):
    """Configurar contexto global para templates"""
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'StrateKaz',
            'current_year': datetime.now().year,
            'version': app.config.get('APP_VERSION', '1.0')
        }
    
    # Registrar filtros y helpers
    from app.utils.template_helpers import register_template_helpers
    register_template_helpers(app)
    app.logger.info("Contexto de templates configurado")

# Crear la aplicación
app = create_app()