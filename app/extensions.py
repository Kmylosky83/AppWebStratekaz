from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_caching import Cache

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
mail = Mail()
migrate = Migrate()
cache = Cache()

