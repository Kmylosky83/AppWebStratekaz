from app.config.database import db
from datetime import datetime

class Tarea(db.Model):
    __tablename__ = 'tareas'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    priority = db.Column(db.String(20), default='medium')  # high, medium, low
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_completada = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True)
    
    # Relaciones con otros modelos
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_tasks')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_tasks')
    empresa = db.relationship('Empresa', backref='tareas')
    
    def __repr__(self):
        return f'<Tarea {self.id}: {self.title}>'
    
    def save(self):
        """Guarda la tarea en la base de datos."""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """Elimina la tarea de la base de datos."""
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        """Convierte la tarea a un diccionario."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_by_id': self.created_by_id,
            'assigned_to_id': self.assigned_to_id,
            'empresa_id': self.empresa_id,
            'created_by': self.created_by.username if self.created_by else None,
            'assigned_to': self.assigned_to.username if self.assigned_to else None
        }
    
    @staticmethod
    def get_by_user(user_id, role='assigned'):
        """
        Obtiene las tareas relacionadas con un usuario.
        
        Args:
            user_id: ID del usuario
            role: Rol del usuario en relación a la tarea ('assigned', 'created', 'all')
        """
        if role == 'assigned':
            return Tarea.query.filter_by(assigned_to_id=user_id).all()
        elif role == 'created':
            return Tarea.query.filter_by(created_by_id=user_id).all()
        elif role == 'all':
            return Tarea.query.filter(
                (Tarea.assigned_to_id == user_id) | (Tarea.created_by_id == user_id)
            ).all()
        return []
    
    @staticmethod
    def get_by_empresa(empresa_id):
        """Obtiene las tareas asociadas a una empresa."""
        return Tarea.query.filter_by(empresa_id=empresa_id).all()
    
    @staticmethod
    def get_by_status(status, user_id=None):
        """
        Obtiene las tareas por estado.
        
        Args:
            status: Estado de las tareas ('pending', 'in_progress', 'completed')
            user_id: Si se proporciona, filtra por usuario asignado
        """
        query = Tarea.query.filter_by(status=status)
        if user_id:
            query = query.filter_by(assigned_to_id=user_id)
        return query.all()
    
    @staticmethod
    def get_by_priority(priority, user_id=None):
        """
        Obtiene las tareas por prioridad.
        
        Args:
            priority: Prioridad de las tareas ('high', 'medium', 'low')
            user_id: Si se proporciona, filtra por usuario asignado
        """
        query = Tarea.query.filter_by(priority=priority)
        if user_id:
            query = query.filter_by(assigned_to_id=user_id)
        return query.all()