from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Añadir las columnas faltantes
    db.engine.execute('ALTER TABLE users ADD COLUMN profession VARCHAR(100)')
    db.engine.execute('ALTER TABLE users ADD COLUMN phone VARCHAR(20)')
    db.engine.execute('ALTER TABLE users ADD COLUMN city VARCHAR(100)')
    print("Base de datos actualizada correctamente")
   