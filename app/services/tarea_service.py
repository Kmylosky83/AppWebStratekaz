from app.models.tarea import Tarea
from app.config.database import db
from datetime import datetime, date

class TareaService:
    """Servicio para gestionar las tareas en el sistema."""
    
    @staticmethod
    def crear_tarea(data, user_id):
        """
        Crea una nueva tarea.
        
        Args:
            data: Diccionario con los datos de la tarea
            user_id: ID del usuario que crea la tarea
        
        Returns:
            Tarea creada o None si hay error
        """
        try:
            # Procesar fecha límite
            due_date = None
            if data.get('due_date'):
                if isinstance(data['due_date'], str):
                    due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
                elif isinstance(data['due_date'], date):
                    due_date = data['due_date']
            
            tarea = Tarea(
                title=data.get('title'),
                description=data.get('description', ''),
                status=data.get('status', 'pending'),
                priority=data.get('priority', 'medium'),
                due_date=due_date,
                created_by_id=user_id,
                assigned_to_id=data.get('assigned_to_id', user_id),
                empresa_id=data.get('empresa_id')
            )
            
            tarea.save()
            return tarea
        except Exception as e:
            print(f"Error al crear tarea: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def actualizar_tarea(tarea_id, data):
        """
        Actualiza una tarea existente.
        
        Args:
            tarea_id: ID de la tarea a actualizar
            data: Diccionario con los datos a actualizar
        
        Returns:
            Tarea actualizada o None si hay error
        """
        try:
            tarea = Tarea.query.get(tarea_id)
            if not tarea:
                return None
            
            # Actualizar campos si están presentes en data
            if 'title' in data:
                tarea.title = data['title']
            if 'description' in data:
                tarea.description = data['description']
            if 'status' in data:
                tarea.status = data['status']
            if 'priority' in data:
                tarea.priority = data['priority']
            if 'due_date' in data and data['due_date']:
                if isinstance(data['due_date'], str):
                    tarea.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
                elif isinstance(data['due_date'], date):
                    tarea.due_date = data['due_date']
            if 'assigned_to_id' in data:
                tarea.assigned_to_id = data['assigned_to_id']
            if 'empresa_id' in data:
                tarea.empresa_id = data['empresa_id']
            
            db.session.commit()
            return tarea
        except Exception as e:
            print(f"Error al actualizar tarea: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def eliminar_tarea(tarea_id):
        """
        Elimina una tarea.
        
        Args:
            tarea_id: ID de la tarea a eliminar
        
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            tarea = Tarea.query.get(tarea_id)
            if not tarea:
                return False
            
            tarea.delete()
            return True
        except Exception as e:
            print(f"Error al eliminar tarea: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def cambiar_estado(tarea_id, nuevo_estado):
        """
        Cambia el estado de una tarea.
        
        Args:
            tarea_id: ID de la tarea
            nuevo_estado: Nuevo estado ('pending', 'in_progress', 'completed')
        
        Returns:
            Tarea actualizada o None si hay error
        """
        try:
            tarea = Tarea.query.get(tarea_id)
            if not tarea:
                return None
            
            tarea.status = nuevo_estado
            db.session.commit()
            return tarea
        except Exception as e:
            print(f"Error al cambiar estado de tarea: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def asignar_tarea(tarea_id, user_id):
        """
        Asigna una tarea a un usuario.
        
        Args:
            tarea_id: ID de la tarea
            user_id: ID del usuario al que se asignará
        
        Returns:
            Tarea actualizada o None si hay error
        """
        try:
            tarea = Tarea.query.get(tarea_id)
            if not tarea:
                return None
            
            tarea.assigned_to_id = user_id
            db.session.commit()
            return tarea
        except Exception as e:
            print(f"Error al asignar tarea: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_estadisticas_usuario(user_id):
        """
        Obtiene estadísticas de tareas para un usuario.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            tareas_asignadas = Tarea.get_by_user(user_id, 'assigned')
            
            pendientes = [t for t in tareas_asignadas if t.status == 'pending']
            en_progreso = [t for t in tareas_asignadas if t.status == 'in_progress']
            completadas = [t for t in tareas_asignadas if t.status == 'completed']
            
            alta_prioridad = [t for t in tareas_asignadas if t.priority == 'high']
            
            # Tareas vencidas
            hoy = date.today()
            vencidas = [t for t in tareas_asignadas if t.due_date and t.due_date < hoy and t.status != 'completed']
            
            return {
                'total': len(tareas_asignadas),
                'pendientes': len(pendientes),
                'en_progreso': len(en_progreso),
                'completadas': len(completadas),
                'alta_prioridad': len(alta_prioridad),
                'vencidas': len(vencidas),
                'tasa_completadas': (len(completadas) / len(tareas_asignadas)) * 100 if tareas_asignadas else 0
            }
        except Exception as e:
            print(f"Error al obtener estadísticas: {str(e)}")
            return {
                'total': 0,
                'pendientes': 0,
                'en_progreso': 0,
                'completadas': 0,
                'alta_prioridad': 0,
                'vencidas': 0,
                'tasa_completadas': 0
            }
    
    @staticmethod
    def buscar_tareas(texto, user_id=None, empresa_id=None):
        """
        Busca tareas por texto.
        
        Args:
            texto: Texto a buscar en título o descripción
            user_id: ID del usuario para filtrar (opcional)
            empresa_id: ID de la empresa para filtrar (opcional)
        
        Returns:
            Lista de tareas que coinciden con la búsqueda
        """
        try:
            query = Tarea.query.filter(
                (Tarea.title.ilike(f'%{texto}%')) | 
                (Tarea.description.ilike(f'%{texto}%'))
            )
            
            if user_id:
                query = query.filter_by(assigned_to_id=user_id)
            
            if empresa_id:
                query = query.filter_by(empresa_id=empresa_id)
            
            return query.all()
        except Exception as e:
            print(f"Error al buscar tareas: {str(e)}")
            return []