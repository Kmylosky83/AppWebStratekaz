from datetime import datetime, timedelta
from app.models.empresa import Empresa
from app.models.user import User

class DashboardService:
    @staticmethod
    def get_stats_for_user(user_id):
        """Obtiene estadísticas para el dashboard de un usuario específico"""
        stats = {
            'total_empresas': 0,
            'total_documentos': 0,
            'pending_tasks': 3,  # Por ahora, valor fijo
            'upcoming_events': [],
            'recent_activity': []
        }
        
        # Obtener empresas del usuario
        empresas = Empresa.get_by_user(user_id)
        stats['total_empresas'] = len(empresas)
        
        # Eventos próximos (ejemplo)
        today = datetime.now()
        stats['upcoming_events'] = [
            {
                'title': 'Revisión SG-SST',
                'date': today + timedelta(days=2),
                'description': 'Revisión trimestral del Sistema de Gestión'
            },
            {
                'title': 'Auditoría Interna',
                'date': today + timedelta(days=5),
                'description': 'Preparación para auditoría de certificación'
            },
            {
                'title': 'Capacitación ISO 45001',
                'date': today + timedelta(days=10),
                'description': 'Capacitación para el personal operativo'
            }
        ]
        
        # Actividad reciente (ejemplo)
        stats['recent_activity'] = [
            {
                'icon': 'fas fa-file-alt',
                'text': 'Se creó nuevo documento "Procedimiento de Compras"',
                'time': 'Hace 2 horas',
                'user': 'Tú'
            },
            {
                'icon': 'fas fa-tasks',
                'text': 'Se completó la tarea "Actualizar matriz de riesgos"',
                'time': 'Ayer',
                'user': 'Ana Gómez'
            },
            {
                'icon': 'fas fa-user-plus',
                'text': 'Se agregó nuevo usuario a la empresa "Consultores ABC"',
                'time': 'Hace 2 días',
                'user': 'Tú'
            }
        ]
        
        return stats