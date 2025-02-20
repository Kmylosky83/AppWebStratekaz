from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer
import logging

def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification')

def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-verification', max_age=expiration)
        return email
    except Exception as e:
        logging.error(f"Error verifying token: {str(e)}")
        return None

def send_verification_email(user):
    try:
        # Por ahora, solo generamos el token y lo mostramos en la consola
        token = generate_verification_token(user.email)
        verify_url = url_for('auth.verificar_email', token=token, _external=True)
        
        # Imprimir en la consola para desarrollo
        print("========== EMAIL DE VERIFICACIÓN ==========")
        print(f"Para: {user.email}")
        print(f"URL de verificación: {verify_url}")
        print("=========================================")
        
        return True
    except Exception as e:
        logging.error(f"Error sending verification email: {str(e)}")
        return False