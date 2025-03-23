from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Añadir las columnas faltantes
    db.engine.execute('ALTER TABLE users ADD COLUMN user_type VARCHAR(20)')
    db.engine.execute('ALTER TABLE users ADD COLUMN company_type VARCHAR(20)')
    db.engine.execute('ALTER TABLE users ADD COLUMN account_verified BOOLEAN DEFAULT 0')
    db.engine.execute('ALTER TABLE users ADD COLUMN last_login DATETIME')
    print("Base de datos actualizada correctamente")