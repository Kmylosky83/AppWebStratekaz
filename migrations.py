from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import create_app
from app.config.database import db

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("Base de datos inicializada correctamente.")