from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from app import create_app
from app.config.database import db

app = create_app()

with app.app_context():
    # Inicializar migraciones
    migrate = Migrate(app, db)
    
    # Realizar migraciones
    try:
        init()
        migrate(message="Inicializar migraciones")
        upgrade()
        print("Migraciones aplicadas correctamente.")
    except Exception as e:
        print(f"Error en las migraciones: {str(e)}")