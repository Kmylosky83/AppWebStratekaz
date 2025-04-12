from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.models.role import Role, Permission, role_permissions

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Campos comunes
    user_type = db.Column(db.String(20), nullable=False)  # 'professional' o 'company'
    phone = db.Column(db.String(20))
    city = db.Column(db.String(100))
    department = db.Column(db.String(100))
    
    # Campos para profesionales
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    profession = db.Column(db.String(100))
    
    # Campos para empresas
    company_type = db.Column(db.String(20))  # 'direct' o 'consultant'
    company_name = db.Column(db.String(200))
    nit = db.Column(db.String(20), unique=True)
    industry = db.Column(db.String(100))
    contact_position = db.Column(db.String(100))
    
    # Relación con roles
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    # Campos de control
    account_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)
    
    def has_permission(self, permission_name):
        """Verifica si el usuario tiene un permiso específico a través de su rol"""
        if not self.role:
            return False
        
        # Buscar el permiso por nombre
        permission = Permission.query.filter_by(name=permission_name).first()
        if not permission:
            return False
        
        # Verificar si el rol tiene ese permiso
        return db.session.query(role_permissions).filter(
            role_permissions.c.role_id == self.role_id,
            role_permissions.c.permission_id == permission.id
        ).count() > 0
    
    def assign_role(self, role_name):
        """Asigna un rol al usuario por nombre"""
        from app.models.role import Role
        role = Role.query.filter_by(name=role_name).first()
        if role:
            self.role_id = role.id
            return True
        return False

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