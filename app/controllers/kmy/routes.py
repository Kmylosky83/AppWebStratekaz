from flask import Blueprint, request, jsonify
import json
from datetime import datetime
import os

kmy_bp = Blueprint('kmy', __name__, url_prefix='/api/kmy')

@kmy_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        context = data.get('context', 'general')
        
        # En esta versión inicial, solo guardamos las interacciones para análisis futuro
        save_interaction(user_message, "Respuesta predefinida", context)
        
        # En el futuro, aquí iría la conexión con la API de Claude u otro modelo de IA
        return jsonify({"success": True, "message": "Procesado correctamente"})
        
    except Exception as e:
        print(f"Error en chat API: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@kmy_bp.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.json
        message_id = data.get('message_id', '')
        message = data.get('message', '')
        feedback = data.get('feedback', '')
        
        # Guardar feedback para aprendizaje futuro
        save_feedback(message_id, message, feedback)
        
        return jsonify({"success": True})
        
    except Exception as e:
        print(f"Error guardando feedback: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

def save_interaction(user_message, response, context):
    """Guarda las interacciones para análisis y mejora futura"""
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'kmy_interactions.jsonl')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'user_message': user_message,
                'response': response,
                'context': context
            }
            f.write(json.dumps(interaction) + '\n')
    except Exception as e:
        print(f"Error guardando interacción: {str(e)}")

def save_feedback(message_id, message, feedback):
    """Guarda el feedback para entrenamiento futuro"""
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'kmy_feedback.jsonl')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            feedback_data = {
                'timestamp': datetime.now().isoformat(),
                'message_id': message_id,
                'message': message,
                'feedback': feedback
            }
            f.write(json.dumps(feedback_data) + '\n')
    except Exception as e:
        print(f"Error guardando feedback: {str(e)}")