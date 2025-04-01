from datetime import datetime, timedelta
from app.models.empresa import Empresa
from app.models.user import User
from app.models.tarea import Tarea
from app.models.formacion import FichaFormacion
from sqlalchemy import func
from app.config.database import db

class DashboardService:
    @staticmethod
    def get_stats_for_user(user_id):
        """Obtiene estadísticas para el dashboard de un usuario específico"""
        stats = {
            'total_empresas': 0,
            'total_documentos': 0,
            'pending_tasks': 0,
            'upcoming_events': [],
            'recent_activity': []
        }
        
        # Obtener empresas del usuario
        empresas = Empresa.get_by_user(user_id)
        stats['total_empresas'] = len(empresas)
        
        # Obtener tareas pendientes
        pending_tasks = Tarea.query.filter(
            (Tarea.assigned_to_id == user_id) & 
            (Tarea.status == 'pending')
        ).count()
        stats['pending_tasks'] = pending_tasks
        
        # Eventos próximos (de fichas de formación)
        today = datetime.now()
        upcoming_events = FichaFormacion.query.filter(
            (FichaFormacion.user_id == user_id) & 
            (FichaFormacion.fecha > today)
        ).order_by(FichaFormacion.fecha).limit(3).all()
        
        stats['upcoming_events'] = [
            {
                'title': evento.titulo,
                'date': evento.fecha,
                'description': evento.descripcion or 'Sin descripción'
            } for evento in upcoming_events
        ]
        
        # Actividad reciente (combinada)
        recent_activity = []
        
        # Actividad de tareas
        recent_tasks = Tarea.query.filter(
            (Tarea.assigned_to_id == user_id)
        ).order_by(
            func.coalesce(Tarea.fecha_completada, Tarea.created_at).desc()
        ).limit(2).all()
        
        recent_activity.extend([
            {
                'icon': 'fas fa-tasks',
                'text': f'Tarea "{tarea.title}" {"completada" if tarea.status == "completed" else "actualizada"}',
                'time': _format_time_ago(tarea.fecha_completada or tarea.created_at),
                'user': 'Tú'
            } for tarea in recent_tasks
        ])
        
        # Actividad de empresas
        recent_empresas = Empresa.query.filter(
            (Empresa.user_id == user_id)
        ).order_by(Empresa.created_at.desc()).limit(1).all()
        
        recent_activity.extend([
            {
                'icon': 'fas fa-building',
                'text': f'Empresa "{empresa.nombre}" registrada',
                'time': _format_time_ago(empresa.created_at),
                'user': 'Tú'
            } for empresa in recent_empresas
        ])
        
        # Ordenar actividad reciente por fecha
        stats['recent_activity'] = sorted(
            recent_activity, 
            key=lambda x: x.get('time', ''), 
            reverse=True
        )[:3]
        
        return stats

def _format_time_ago(date):
    """Formatea una fecha en un string de tiempo relativo"""
    if not date:
        return 'Hace un momento'
    
    now = datetime.now()
    diff = now - date
    
    if diff.days > 30:
        return f'Hace {diff.days // 30} mes{"es" if diff.days // 30 > 1 else ""}'
    elif diff.days > 0:
        return f'Hace {diff.days} día{"s" if diff.days > 1 else ""}'
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f'Hace {hours} hora{"s" if hours > 1 else ""}'
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f'Hace {minutes} minuto{"s" if minutes > 1 else ""}'
    else:
        return 'Hace un momento'