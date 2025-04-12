from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_caching import Cache
from flask import current_app
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
socketio = SocketIO()
mail = Mail()
cache = Cache()

def init_extensions(app):
    """Inicializa todas las extensiones de Flask"""
    try:
        logger.info("Iniciando configuración de extensiones...")
        
        # Inicializar SQLAlchemy
        db.init_app(app)
        logger.info("✅ SQLAlchemy inicializado")
        
        # Inicializar otras extensiones
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        logger.info("✅ Login manager inicializado")
        
        mail.init_app(app)
        logger.info("✅ Mail configurado")
        
        migrate.init_app(app, db)
        logger.info("✅ Migraciones configuradas")
        
        cache.init_app(app)
        logger.info("✅ Cache configurado")
        
        socketio.init_app(app)
        register_socketio_events()
        logger.info("✅ SocketIO configurado")
        
        # Crear tablas si no existen (solo en desarrollo)
        if app.config['DEBUG']:
            with app.app_context():
                db.create_all()
                logger.info("✅ Tablas de base de datos verificadas")
        
        logger.info("✅ Todas las extensiones inicializadas correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error al inicializar extensiones: {str(e)}")
        raise

def register_socketio_events():
    """Registrar eventos básicos de SocketIO"""
    @socketio.on('connect')
    def handle_connect():
        logger.info('Cliente conectado via SocketIO')

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info('Cliente desconectado via SocketIO')