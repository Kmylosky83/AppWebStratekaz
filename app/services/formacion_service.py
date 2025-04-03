from app.models.formacion import FichaFormacion, ListaAsistencia
from app.config.database import db
import uuid
from datetime import datetime

class FormacionService:
    @staticmethod
    def generar_codigo_documento(tipo='FORM'):
        """
        Genera un código de documento consecutivo
        Ejemplo: FORM-2024-001
        """
        # Obtener el último documento para incrementar el consecutivo
        ultimo_documento = FichaFormacion.query.order_by(FichaFormacion.id.desc()).first()
        
        if ultimo_documento:
            # Extraer último número y incrementar
            try:
                ultimo_numero = int(ultimo_documento.codigo.split('-')[-1])
                nuevo_numero = f"{ultimo_numero + 1:03d}"
            except:
                nuevo_numero = "001"
        else:
            nuevo_numero = "001"
        
        return f"{tipo}-{datetime.now().year}-{nuevo_numero}"
    
    @staticmethod
    def crear_ficha_formacion(datos):
        """
        Crear una nueva ficha de formación
        """
        codigo = FormacionService.generar_codigo_documento()
        
        ficha = FichaFormacion(
            titulo=datos['titulo'],
            descripcion=datos.get('descripcion', ''),
            fecha=datos['fecha'],
            lugar=datos.get('lugar', ''),
            duracion=datos.get('duracion', ''),
            responsable=datos['responsable'],
            codigo=codigo
        )
        
        # Lógica para guardar objetivos, recursos, etc.
        
        db.session.add(ficha)
        db.session.commit()
        
        return ficha
    
    @staticmethod
    def generar_enlace_externo():
        """
        Genera un enlace único para registro externo
        """
        return str(uuid.uuid4())