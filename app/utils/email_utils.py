from flask import current_app, url_for, render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from app.extensions import mail
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def send_email(to: str, subject: str, template: str, **kwargs: Dict[str, Any]) -> bool:
    """
    Enviar correo electrónico usando templates HTML
    
    Args:
        to: Dirección de correo del destinatario
        subject: Asunto del correo
        template: Ruta al template HTML
        **kwargs: Variables para el template
    """
    try:
        msg = Message(
            subject,
            recipients=[to],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Renderizar templates con valores por defecto
        context = {
            'app_name': 'StrateKaz',
            'current_year': current_app.config.get('CURRENT_YEAR', 2025),
            **kwargs
        }
        
        msg.html = render_template(f'email/{template}.html', **context)
        # Intentar cargar versión texto plano si existe
        try:
            msg.body = render_template(f'email/{template}.txt', **context)
        except:
            # Si no existe versión .txt, crear una básica desde el HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(msg.html, 'html.parser')
            msg.body = soup.get_text()
        
        mail.send(msg)
        logger.info(f"Correo enviado exitosamente a {to}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando correo a {to}: {str(e)}")
        return False

def generate_verification_token(email: str) -> str:
    """
    Generar token de verificación para email
    
    Args:
        email: Correo electrónico a verificar
    Returns:
        str: Token generado
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification')

def verify_token(token: str, expiration: int = 3600) -> Optional[str]:
    """
    Verificar token de email
    
    Args:
        token: Token a verificar
        expiration: Tiempo de expiración en segundos (default 1 hora)
    Returns:
        Optional[str]: Email si el token es válido, None si no
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token, 
            salt='email-verification',
            max_age=expiration
        )
        return email
    except Exception as e:
        logger.error(f"Error verificando token: {str(e)}")
        return None

def send_verification_email(user) -> bool:
    """
    Enviar email de verificación al usuario
    
    Args:
        user: Usuario al que enviar la verificación
    Returns:
        bool: True si se envió correctamente, False si no
    """
    try:
        token = generate_verification_token(user.email)
        verify_url = url_for(
            'auth.verificar_email',
            token=token,
            _external=True
        )
        
        return send_email(
            to=user.email,
            subject='Verifica tu cuenta - StrateKaz',
            template='verificacion_email',
            user=user,
            verify_url=verify_url
        )
        
    except Exception as e:
        logger.error(f"Error enviando email de verificación: {str(e)}")
        return False

def send_reset_password_email(user) -> bool:
    """
    Enviar email de recuperación de contraseña
    
    Args:
        user: Usuario que solicitó el reset
    """
    try:
        token = generate_verification_token(user.email)
        reset_url = url_for(
            'auth.reset_password',
            token=token,
            _external=True
        )
        
        return send_email(
            to=user.email,
            subject='Recuperación de Contraseña - StrateKaz',
            template='reset_password',
            user=user,
            reset_url=reset_url
        )
        
    except Exception as e:
        logger.error(f"Error sending reset password email: {str(e)}")
        return False

def send_welcome_email(user) -> bool:
    """
    Enviar email de bienvenida al nuevo usuario
    
    Args:
        user: Usuario recién registrado
    """
    try:
        return send_email(
            to=user.email,
            subject='¡Bienvenido a StrateKaz!',
            template='welcome_email',
            user=user
        )
        
    except Exception as e:
        logger.error(f"Error sending welcome email: {str(e)}")
        return False