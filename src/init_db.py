import sys
import os

# Agregar la raíz del proyecto al path de ejecución de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infrastructure.database.session import engine, Base
from src.domain.models.incident import IncidentModel

def initialize_database():
    """Crea todas las tablas definidas en los modelos ORM dentro de PostgreSQL."""
    print("Conectando con la base de datos de CYCLOPS...")
    try:
        # Crea las tablas si no existen en la base de datos
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas exitosamente en PostgreSQL.")
        print("Tabla 'incidents' vinculada correctamente.")
    except Exception as e:
        print(f"Error al conectar o crear tablas en PostgreSQL: {e}")

if __name__ == "__main__":
    initialize_database()