from datetime import datetime, timedelta
from app.models.empresa import Empresa

class DashboardService:
    """Servicio para proporcionar datos al dashboard."""
    
    @staticmethod
    def get_user_stats(user_id):
        """Obtiene estadísticas para el dashboard del usuario."""
        return {
            'pending_tasks': DashboardService.get_pending_tasks_count(user_id),
            'upcoming_events': DashboardService.get_upcoming_events(user_id),
            'recent_activity': DashboardService.get_recent_activity(user_id)
        }
    
    @staticmethod
    def get_pending_tasks_count(user_id):
        """Obtiene el número de tareas pendientes."""
        # En una versión futura, esto consultaría un modelo de tareas real
        # Por ahora, devolvemos valores simulados
        return 3
    
    @staticmethod
    def get_upcoming_events(user_id):
        """Obtiene eventos próximos para el usuario."""
        # Simulamos eventos próximos hasta que tengamos un modelo real
        today = datetime.now()
        
        events = [
            {
                'title': 'Actualización de Matriz de Riesgos',
                'date': today + timedelta(days=2, hours=3, minutes=30)
            },
            {
                'title': 'Reunión de Seguimiento',
                'date': today + timedelta(days=5, hours=1)
            }
        ]
        
        return events
    
    @staticmethod
    def get_recent_activity(user_id):
        """Obtiene la actividad reciente del usuario."""
        # Simulamos actividad reciente
        now = datetime.now()
        
        activities = [
            {
                'icon': 'fas fa-user-edit',
                'text': 'Actualizaste tu perfil',
                'time': '5 minutos atrás'
            },
            {
                'icon': 'fas fa-sign-in-alt',
                'text': 'Iniciaste sesión desde un nuevo dispositivo',
                'time': '2 horas atrás'
            },
            {
                'icon': 'fas fa-file-alt',
                'text': 'Creaste un nuevo documento',
                'time': '1 día atrás'
            }
        ]
        
        return activities
    
    @staticmethod
    def get_company_info(user_id):
        """Obtiene información de empresas asociadas al usuario."""
        companies = Empresa.get_by_user(user_id)
        return companies