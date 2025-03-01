from app.config.database import db
from datetime import datetime

class Tarea(db.Model):
    __tablename__ = 'tareas'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, en_progreso, completada, cancelada
    prioridad = db.Column(db.String(10), default='media')   # alta, media, baja
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime, nullable=True)
    fecha_completada = db.Column(db.DateTime, nullable=True)
    
    # Relación con el usuario asignado
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tareas', lazy=True))
    
    # Relación opcional con una empresa
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True)
    empresa = db.relationship('Empresa', backref=db.backref('tareas', lazy=True))
    
    def __repr__(self):
        return f'<Tarea {self.titulo}>'
    
    def to_dict(self):
        """Convierte la tarea a un diccionario para API/JSON"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'prioridad': self.prioridad,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'fecha_completada': self.fecha_completada.isoformat() if self.fecha_completada else None,
            'user_id': self.user_id,
            'empresa_id': self.empresa_id
        }
    
    @property
    def esta_vencida(self):
        """Determina si la tarea está vencida"""
        if not self.fecha_vencimiento:
            return False
        if self.estado == 'completada':
            return False
        return datetime.utcnow() > self.fecha_vencimiento
    
    @property
    def dias_restantes(self):
        """Calcula los días restantes hasta la fecha de vencimiento"""
        if not self.fecha_vencimiento:
            return None
        if self.estado == 'completada':
            return 0
        
        delta = self.fecha_vencimiento - datetime.utcnow()
        return delta.days