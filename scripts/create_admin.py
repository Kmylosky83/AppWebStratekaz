from flask import Flask
import os
import sys

# Añadir el directorio raíz al path para importar desde app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.role import Role

def create_super_admin():
    """
    Crea un usuario super administrador en la base de datos
    """
    app = create_app('development')
    
    with app.app_context():
        # Verificar si ya existe un superadmin
        admin = User.query.filter_by(email='admin@stratekaz.com').first()
        if admin:
            print("El usuario super administrador ya existe.")
            return
        
        # Obtener el rol de super_admin
        role = Role.query.filter_by(name='super_admin').first()
        if not role:
            print("El rol super_admin no existe. Asegúrate de que los roles están inicializados.")
            return
        
        # Crear usuario super administrador
        admin = User(
            username='admin',
            email='admin@stratekaz.com',
            user_type='professional',
            first_name='Admin',
            last_name='StrateKaz',
            role_id=role.id,
            account_verified=True
        )
        admin.set_password('Admin@123')
        
        try:
            db.session.add(admin)
            db.session.commit()
            print("Super administrador creado con éxito.")
            print("Email: admin@stratekaz.com")
            print("Contraseña: Admin@123")
        except Exception as e:
            db.session.rollback()
            print(f"Error creando super administrador: {str(e)}")

if __name__ == '__main__':
    create_super_admin()