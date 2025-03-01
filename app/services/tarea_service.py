from datetime import datetime
from app.models.tarea import Tarea
from app.config.database import db

class TareaService:
    @staticmethod
    def get_tareas_pendientes(user_id, limit=5):
        """
        Obtiene las tareas pendientes de un usuario
        
        Args:
            user_id: ID del usuario
            limit: Número máximo de tareas a devolver
            
        Returns:
            list: Lista de tareas pendientes
        """
        # Esta es una implementación básica, puedes expandirla según tus necesidades
        try:
            tareas = Tarea.query.filter_by(
                user_id=user_id,
                estado='pendiente'
            ).order_by(Tarea.fecha_vencimiento.asc()).limit(limit).all()
            
            return tareas
        except Exception as e:
            print(f"Error obteniendo tareas pendientes: {str(e)}")
            return []
    
    @staticmethod
    def crear_tarea(user_id, titulo, descripcion, fecha_vencimiento, prioridad='media'):
        """
        Crea una nueva tarea
        
        Args:
            user_id: ID del usuario asignado
            titulo: Título de la tarea
            descripcion: Descripción detallada
            fecha_vencimiento: Fecha límite
            prioridad: Nivel de prioridad (alta, media, baja)
            
        Returns:
            Tarea: La tarea creada o None si hay error
        """
        try:
            tarea = Tarea(
                titulo=titulo,
                descripcion=descripcion,
                fecha_creacion=datetime.now(),
                fecha_vencimiento=fecha_vencimiento,
                estado='pendiente',
                prioridad=prioridad,
                user_id=user_id
            )
            
            db.session.add(tarea)
            db.session.commit()
            return tarea
        except Exception as e:
            db.session.rollback()
            print(f"Error creando tarea: {str(e)}")
            return None
    
    @staticmethod
    def cambiar_estado_tarea(tarea_id, nuevo_estado):
        """
        Cambia el estado de una tarea
        
        Args:
            tarea_id: ID de la tarea
            nuevo_estado: Estado nuevo (pendiente, en_progreso, completada, cancelada)
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            tarea = Tarea.query.get(tarea_id)
            if not tarea:
                return False
                
            tarea.estado = nuevo_estado
            if nuevo_estado == 'completada':
                tarea.fecha_completada = datetime.now()
                
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error actualizando estado de tarea: {str(e)}")
            return False