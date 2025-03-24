from app.config.database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_login import current_user

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    #login_attempts = db.Column(db.Integer, default=0)
    #last_attempt_time = db.Column(db.DateTime, nullable=True)
    #is_locked = db.Column(db.Boolean, default=False)
    
    user_type = db.Column(db.String(20), nullable=True)  # 'professional' o 'company'
    company_type = db.Column(db.String(20), nullable=True)  # 'direct' o 'consultant'
    account_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Campos adicionales para información personal
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    company_name = db.Column(db.String(200), nullable=True)
    nit = db.Column(db.String(20), nullable=True)
    profession = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(100), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)
    
    def increment_login_attempts(self):
        """Incrementa los intentos de login y bloquea si es necesario"""
        #now = datetime.utcnow()
        
        # Resetear intentos si han pasado más de 15 minutos
        #if (self.last_attempt_time and 
        #    now - self.last_attempt_time > timedelta(minutes=15)):
        #    self.login_attempts = 0
        
        #self.login_attempts += 1
        #self.last_attempt_time = now
        
        # Bloquear después de 5 intentos fallidos
        #if self.login_attempts >= 5:
        #    self.is_locked = True
        
        #db.session.commit()

    def reset_login_attempts(self):
        """Resetea los intentos de login"""
        #self.login_attempts = 0
        #self.is_locked = False
        #self.last_attempt_time = None
        #db.session.commit()

    @staticmethod
    def validate_password_strength(password):
        """Validación robusta de contraseña"""
        if len(password) < 8:
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char.isupper() for char in password):
            return False
        if not any(char.islower() for char in password):
            return False
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
            return False
        return True
    
    @staticmethod
    def generate_unique_username(base_username):
        """Genera un nombre de usuario único basado en el email o nombre proporcionado"""
        username = base_username
        counter = 1
        
        # Verificar si existe y añadir un número hasta encontrar uno único
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
            
        return username