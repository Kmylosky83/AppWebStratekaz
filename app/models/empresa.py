from app.config.database import db
from datetime import datetime

class Empresa(db.Model):
    __tablename__ = 'empresas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ruc = db.Column(db.String(20), unique=True, nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relación con el usuario
    user = db.relationship('User', backref=db.backref('empresas', lazy=True))
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    @staticmethod
    def get_by_user(user_id):
        return Empresa.query.filter_by(user_id=user_id).all()
        
    def __repr__(self):
        return f'<Empresa {self.nombre}>'