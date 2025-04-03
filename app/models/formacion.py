from app.config.database import db
from datetime import datetime
from sqlalchemy.orm import relationship

class FichaFormacion(db.Model):
    __tablename__ = 'fichas_formacion'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    lugar = db.Column(db.String(200), nullable=True)
    duracion = db.Column(db.String(50), nullable=True)  # Ejemplo: "2 horas"
    responsable = db.Column(db.String(100), nullable=True)
    objetivos = db.Column(db.Text, nullable=True)
    codigo = db.Column(db.String(50), nullable=True)  # Código para control documental
    
    # Relaciones
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True)
    
    # Relación con la lista de asistencia
    listas_asistencia = relationship("ListaAsistencia", back_populates="ficha", cascade="all, delete-orphan")
    
    # Relación con las preguntas
    preguntas = relationship("PreguntaFormacion", back_populates="ficha", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<FichaFormacion {self.id}: {self.titulo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'fecha': self.fecha.strftime("%Y-%m-%d %H:%M") if self.fecha else None,
            'lugar': self.lugar,
            'duracion': self.duracion,
            'responsable': self.responsable,
            'objetivos': self.objetivos,
            'codigo': self.codigo,
            'user_id': self.user_id,
            'empresa_id': self.empresa_id
        }

class PreguntaFormacion(db.Model):
    __tablename__ = 'preguntas_formacion'
    
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(500), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # 'opcion_multiple', 'texto', 'si_no'
    opciones = db.Column(db.Text, nullable=True)  # JSON string con opciones para opción múltiple
    
    # Relación con la ficha
    ficha_id = db.Column(db.Integer, db.ForeignKey('fichas_formacion.id'), nullable=False)
    ficha = relationship("FichaFormacion", back_populates="preguntas")
    
    # Relación con las respuestas
    respuestas = relationship("RespuestaFormacion", back_populates="pregunta", cascade="all, delete-orphan")

class ListaAsistencia(db.Model):
    __tablename__ = 'listas_asistencia'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='activa')  # activa, cerrada
    enlace_compartible = db.Column(db.String(200), nullable=True)
    es_externo = db.Column(db.Boolean, default=False)
    email_externo = db.Column(db.String(100), nullable=True)
    
    # Relación con la ficha
    ficha_id = db.Column(db.Integer, db.ForeignKey('fichas_formacion.id'), nullable=False)
    ficha = relationship("FichaFormacion", back_populates="listas_asistencia")
    
    # Relación con los asistentes
    asistentes = relationship("Asistente", back_populates="lista", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<ListaAsistencia {self.id} para Ficha {self.ficha_id}>'

class Asistente(db.Model):
    __tablename__ = 'asistentes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20), nullable=True)
    cargo = db.Column(db.String(100), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    firma_data = db.Column(db.Text, nullable=True)  # Datos de la firma digital (base64)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con la lista
    lista_id = db.Column(db.Integer, db.ForeignKey('listas_asistencia.id'), nullable=False)
    lista = relationship("ListaAsistencia", back_populates="asistentes")
    
    # Relación con las respuestas
    respuestas = relationship("RespuestaFormacion", back_populates="asistente", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Asistente {self.id}: {self.nombre}>'

class RespuestaFormacion(db.Model):
    __tablename__ = 'respuestas_formacion'
    
    id = db.Column(db.Integer, primary_key=True)
    respuesta = db.Column(db.Text, nullable=True)
    
    # Relaciones
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas_formacion.id'), nullable=False)
    asistente_id = db.Column(db.Integer, db.ForeignKey('asistentes.id'), nullable=False)
    
    pregunta = relationship("PreguntaFormacion", back_populates="respuestas")
    asistente = relationship("Asistente", back_populates="respuestas")