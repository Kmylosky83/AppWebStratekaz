from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Añadir las columnas faltantes
    db.engine.execute('ALTER TABLE users ADD COLUMN first_name VARCHAR(100)')
    db.engine.execute('ALTER TABLE users ADD COLUMN last_name VARCHAR(100)')
    db.engine.execute('ALTER TABLE users ADD COLUMN company_name VARCHAR(200)')
    db.engine.execute('ALTER TABLE users ADD COLUMN nit VARCHAR(20)')
    print("Base de datos actualizada correctamente")