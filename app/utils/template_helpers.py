from flask import current_app, g
from flask_login import current_user

def get_user_permissions():
    """
    Obtiene los permisos del usuario actual para usar en templates
    """
    if not current_user.is_authenticated or not current_user.role:
        return []
    
    # Si ya calculamos los permisos en esta sesión, devolver los almacenados
    if hasattr(g, 'user_permissions'):
        return g.user_permissions
    
    # Importar aquí para evitar importaciones circulares
    from app.utils.role_utils import get_user_permissions
    
    # Obtener permisos y almacenarlos en el contexto de la aplicación
    permissions = get_user_permissions(current_user.id)
    g.user_permissions = [p.name for p in permissions]
    
    return g.user_permissions


def has_permission(permission_name):
    """
    Verifica si el usuario actual tiene un permiso específico
    Para usar en templates
    """
    if not current_user.is_authenticated:
        return False
    
    permissions = get_user_permissions()
    return permission_name in permissions

def register_template_helpers(app):
    """
    Registra helpers para usar en templates
    """
    @app.context_processor
    def utility_processor():
        return {
            'has_permission': has_permission,
            'get_user_permissions': get_user_permissions
        }