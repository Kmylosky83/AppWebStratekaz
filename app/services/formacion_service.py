from app.models.formacion import FichaFormacion, ListaAsistencia
from app.config.database import db
from datetime import datetime
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from flask import render_template, current_app
from typing import Optional, Dict, Any
from PIL import Image
import uuid
import tempfile
import os
import io
import logging
import time

# Configurar logging
logger = logging.getLogger(__name__)

# Definir estilos CSS para PDF
PDF_STYLES = """
    @page {
        size: a4 portrait;
        margin: 2cm 1.5cm;
        @top-center {
            content: element(header);
        }
        @bottom-center {
            content: "Página " counter(page) " de " counter(pages);
            font-size: 9pt;
        }
    }
    
    /* Estilos existentes */
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #333333;
    }
    
    .header {
        position: running(header);
        margin-bottom: 1cm;
        border-bottom: 2px solid #007bff;
        padding-bottom: 1cm;
    }
    
    /* ...resto de estilos sin cambios... */
"""

class PDFGenerationError(Exception):
    """Excepción personalizada para errores en generación de PDF"""
    pass

class FormacionService:
    @staticmethod
    def generar_codigo_documento(tipo: str = 'FORM') -> str:
        """Genera un código de documento consecutivo"""
        tipos_validos = ['FORM', 'EVAL', 'CERT']
        if tipo not in tipos_validos:
            raise ValueError(f"Tipo de documento no válido. Debe ser uno de: {tipos_validos}")
            
        ultimo_documento = FichaFormacion.query.order_by(FichaFormacion.id.desc()).first()
        
        try:
            if ultimo_documento:
                ultimo_numero = int(ultimo_documento.codigo.split('-')[-1])
                nuevo_numero = f"{ultimo_numero + 1:03d}"
            else:
                nuevo_numero = "001"
            
            return f"{tipo}-{datetime.now().year}-{nuevo_numero}"
        except Exception as e:
            logger.error(f"Error generando código: {str(e)}")
            raise

    @staticmethod
    def crear_ficha_formacion(datos: Dict[str, Any]) -> FichaFormacion:
        """Crear una nueva ficha de formación"""
        try:
            campos_requeridos = ['titulo', 'fecha', 'responsable']
            if not all(campo in datos for campo in campos_requeridos):
                raise ValueError("Faltan campos requeridos")

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
            
            db.session.add(ficha)
            db.session.commit()
            logger.info(f"Ficha creada exitosamente: {codigo}")
            
            return ficha
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando ficha: {str(e)}")
            raise ValueError(f"Error creando ficha: {str(e)}")

    @staticmethod
    def generar_enlace_externo() -> str:
        """Genera un enlace único para registro externo"""
        return str(uuid.uuid4())

    @staticmethod
    def optimizar_imagen(imagen_path: str) -> bytes:
        """Optimiza una imagen para el PDF"""
        try:
            with Image.open(imagen_path) as img:
                if img.size[0] > 1000 or img.size[1] > 1000:
                    img.thumbnail((1000, 1000))
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True)
                return buffer.getvalue()
        except Exception as e:
            logger.error(f"Error optimizando imagen: {str(e)}")
            raise

    @staticmethod
    def generar_pdf_acta(ficha: FichaFormacion, lista_asistencia: ListaAsistencia) -> str:
        """Genera un PDF del acta de formación"""
        temp_file: Optional[str] = None
        
        try:
            # Validaciones
            if not isinstance(ficha, FichaFormacion):
                raise ValueError("El parámetro 'ficha' debe ser una instancia de FichaFormacion")
            if not isinstance(lista_asistencia, ListaAsistencia):
                raise ValueError("El parámetro 'lista_asistencia' debe ser una instancia de ListaAsistencia")
            if not ficha.titulo or not ficha.fecha:
                raise ValueError("La ficha debe tener título y fecha")
            if not lista_asistencia.asistentes:
                raise ValueError("La lista de asistencia no puede estar vacía")

            logger.info(f"Iniciando generación de PDF para ficha {ficha.codigo}")

            # Renderizar HTML
            html_string = render_template(
                'formacion/pdf_acta.html',
                ficha=ficha,
                lista=lista_asistencia
            )

            # Configurar fuentes y generar PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                temp_file = tmp.name
                
                HTML(string=html_string).write_pdf(
                    temp_file,
                    stylesheets=[CSS(string=PDF_STYLES)],
                    font_config=FontConfiguration()
                )
                
                logger.info(f"PDF generado exitosamente: {temp_file}")
                return temp_file

        except Exception as e:
            logger.error(f"Error generando PDF para ficha {ficha.codigo}: {str(e)}")
            
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except OSError as ose:
                    logger.error(f"Error eliminando archivo temporal {temp_file}: {str(ose)}")
            
            raise PDFGenerationError(f"Error generando PDF: {str(e)}")

    @staticmethod
    def limpiar_archivos_temporales() -> None:
        """Limpia archivos PDF temporales antiguos"""
        temp_dir = tempfile.gettempdir()
        try:
            for file in os.listdir(temp_dir):
                if file.startswith('acta_') and file.endswith('.pdf'):
                    file_path = os.path.join(temp_dir, file)
                    try:
                        if os.path.getmtime(file_path) < (time.time() - 86400):
                            os.unlink(file_path)
                            logger.info(f"Archivo temporal eliminado: {file_path}")
                    except OSError as e:
                        logger.warning(f"No se pudo eliminar archivo temporal {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error limpiando archivos temporales: {str(e)}")