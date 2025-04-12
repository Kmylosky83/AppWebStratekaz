from app.models.role import Role, Permission, role_permissions
from app.models.user import User
from app.extensions import db
from flask import current_app

def init_roles_and_permissions():
    """
    Inicializa los roles y permisos por defecto en la base de datos
    """
    # Definir los roles principales
    roles = [
        {
            'name': 'super_admin',
            'description': 'Administración centralizada del sistema completo',
            'role_type': 'super_admin'
        },
        {
            'name': 'professional',
            'description': 'Consultor que trabaja de forma autónoma',
            'role_type': 'professional'
        },
        {
            'name': 'consultant_company',
            'description': 'Organización dedicada a consultoría en sistemas de gestión',
            'role_type': 'consultant_company'
        },
        {
            'name': 'direct_company_admin',
            'description': 'Administrador de una empresa directa',
            'role_type': 'direct_company'
        },
        {
            'name': 'direct_company_editor',
            'description': 'Editor de una empresa directa',
            'role_type': 'direct_company'
        },
        {
            'name': 'direct_company_viewer',
            'description': 'Visualizador de una empresa directa',
            'role_type': 'direct_company'
        },
        {
            'name': 'consultant',
            'description': 'Miembro de una Empresa Consultora',
            'role_type': 'consultant'
        },
        {
            'name': 'company_member',
            'description': 'Usuario dentro de una Empresa Directa',
            'role_type': 'company_member'
        }
    ]
    
    # Definir los permisos por módulos
    permissions = [
        # Administración del Sistema
        {
            'name': 'admin_users',
            'description': 'Gestión de usuarios',
            'module': 'system'
        },
        {
            'name': 'admin_config',
            'description': 'Configuración global',
            'module': 'system'
        },
        {
            'name': 'admin_modules',
            'description': 'Parametrización de módulos',
            'module': 'system'
        },
        
        # Gestión Documental
        {
            'name': 'docs_create',
            'description': 'Creación de documentos',
            'module': 'documents'
        },
        {
            'name': 'docs_edit',
            'description': 'Edición de documentos',
            'module': 'documents'
        },
        {
            'name': 'docs_approve',
            'description': 'Aprobación de documentos',
            'module': 'documents'
        },
        {
            'name': 'docs_view',
            'description': 'Visualización de documentos',
            'module': 'documents'
        },
        
        # Gestión de Procesos
        {
            'name': 'process_create',
            'description': 'Creación/edición de procesos',
            'module': 'processes'
        },
        {
            'name': 'process_assign',
            'description': 'Asignación de responsables',
            'module': 'processes'
        },
        {
            'name': 'process_indicators',
            'description': 'Gestión de indicadores',
            'module': 'processes'
        },
        
        # Auditorías
        {
            'name': 'audit_schedule',
            'description': 'Programación de auditorías',
            'module': 'audits'
        },
        {
            'name': 'audit_execute',
            'description': 'Ejecución de auditorías',
            'module': 'audits'
        },
        {
            'name': 'audit_findings',
            'description': 'Gestión de hallazgos',
            'module': 'audits'
        },
        {
            'name': 'audit_actions',
            'description': 'Seguimiento de planes de acción',
            'module': 'audits'
        },
        
        # Formación
        {
            'name': 'training_manage',
            'description': 'Gestión de formaciones',
            'module': 'training'
        },
        {
            'name': 'training_participate',
            'description': 'Participar en formaciones',
            'module': 'training'
        }
    ]
    
    # Crear los roles si no existen
    for role_data in roles:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(**role_data)
            db.session.add(role)
            current_app.logger.info(f"Rol creado: {role_data['name']}")
    
    # Crear los permisos si no existen
    for perm_data in permissions:
        perm = Permission.query.filter_by(name=perm_data['name']).first()
        if not perm:
            perm = Permission(**perm_data)
            db.session.add(perm)
            current_app.logger.info(f"Permiso creado: {perm_data['name']}")
    
    # Guardar para obtener los IDs
    db.session.commit()
    
    # Asignar permisos a roles
    assign_default_permissions()
    
    return True

def assign_default_permissions():
    """
    Asigna los permisos por defecto a cada rol
    """
    # Obtener roles
    super_admin = Role.query.filter_by(name='super_admin').first()
    professional = Role.query.filter_by(name='professional').first()
    consultant_company = Role.query.filter_by(name='consultant_company').first()
    direct_company_admin = Role.query.filter_by(name='direct_company_admin').first()
    direct_company_editor = Role.query.filter_by(name='direct_company_editor').first()
    direct_company_viewer = Role.query.filter_by(name='direct_company_viewer').first()
    consultant = Role.query.filter_by(name='consultant').first()
    company_member = Role.query.filter_by(name='company_member').first()
    
    # Super Admin: todos los permisos
    all_permissions = Permission.query.all()
    for perm in all_permissions:
        assign_permission_to_role(super_admin.id, perm.id)
    
    # Professional: permisos de gestión de empresas cliente
    professional_perms = ['docs_create', 'docs_edit', 'docs_approve', 'docs_view', 
                         'process_create', 'process_assign', 'process_indicators',
                         'audit_schedule', 'audit_execute', 'audit_findings', 'audit_actions',
                         'training_manage']
    
    assign_permissions_by_name(professional.id, professional_perms)
    
    # Company Consultant: similar a Professional pero con más controles
    consultant_company_perms = professional_perms + ['admin_users']
    assign_permissions_by_name(consultant_company.id, consultant_company_perms)
    
    # Direct Company Admin
    direct_company_admin_perms = ['docs_create', 'docs_edit', 'docs_approve', 'docs_view',
                                 'process_create', 'process_assign', 'process_indicators',
                                 'audit_schedule', 'audit_execute', 'audit_findings', 'audit_actions',
                                 'admin_users', 'training_manage']
    
    assign_permissions_by_name(direct_company_admin.id, direct_company_admin_perms)
    
    # Direct Company Editor
    direct_company_editor_perms = ['docs_create', 'docs_edit', 'docs_view',
                                  'process_create', 'process_indicators',
                                  'audit_findings', 'audit_actions',
                                  'training_participate']
    
    assign_permissions_by_name(direct_company_editor.id, direct_company_editor_perms)
    
    # Direct Company Viewer
    direct_company_viewer_perms = ['docs_view', 'training_participate']
    assign_permissions_by_name(direct_company_viewer.id, direct_company_viewer_perms)
    
    # Consultant
    consultant_perms = ['docs_create', 'docs_edit', 'docs_view',
                       'process_create', 'process_indicators',
                       'audit_execute', 'audit_findings',
                       'training_manage']
    
    assign_permissions_by_name(consultant.id, consultant_perms)
    
    # Company Member
    company_member_perms = ['docs_view', 'training_participate']
    assign_permissions_by_name(company_member.id, company_member_perms)
    
    db.session.commit()

def assign_permissions_by_name(role_id, permission_names):
    """
    Asigna permisos a un rol usando los nombres de los permisos
    """
    for perm_name in permission_names:
        perm = Permission.query.filter_by(name=perm_name).first()
        if perm:
            assign_permission_to_role(role_id, perm.id)

def assign_permission_to_role(role_id, permission_id):
    """
    Asigna un permiso específico a un rol
    """
    # Verificar si la asignación ya existe
    exists = db.session.query(role_permissions).filter_by(
        role_id=role_id, permission_id=permission_id).count() > 0
    
    if not exists:
        # Insertar en la tabla de asociación
        stmt = role_permissions.insert().values(
            role_id=role_id,
            permission_id=permission_id
        )
        db.session.execute(stmt)

def get_user_permissions(user_id):
    """
    Obtiene todos los permisos de un usuario basados en su rol
    """
    user = User.query.get(user_id)
    if not user or not user.role:
        return []
    
    # Consulta para obtener los permisos del rol del usuario
    stmt = db.session.query(Permission).join(
        role_permissions, 
        Permission.id == role_permissions.c.permission_id
    ).filter(
        role_permissions.c.role_id == user.role_id
    )
    
    return stmt.all()