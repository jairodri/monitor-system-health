from utils import connect_to_oracle
from sqlalchemy import text

def check_database(db_type: str, db_config: dict) ->  tuple[bool, str]:
    """
    Verifica la salud de una base de datos Oracle.

    Args:
        db_type (str): Tipo de base de datos (de momento solo 'oracle').
        db_config (dict): Configuración de la base de datos.

    Returns:
        str: Número de tareas activas o un mensaje de error.
    """
    if db_type.lower() != 'oracle':
        return "ERROR: Tipo de base de datos no soportado."

    try:
        # Conectar a la base de datos usando SQLAlchemy
        engine = connect_to_oracle(
            host=db_config['host'],
            port=db_config['port'],
            service_name=db_config['service_name'],
            username=db_config['username'],
            password=db_config['password']
        )

        if not engine:
            return False, "ERROR: No se pudo conectar a la base de datos."
 
        with engine.connect() as connection:
            # Ejecutar una consulta para contar las tareas activas
            result = connection.execute(text("SELECT COUNT(*) FROM server_action"))
            active_tasks = result.scalar()  # Obtener el número de tareas activas

        return True, f"{active_tasks} tareas pendientes en server_action."

    except Exception as e:
        return False, f"ERROR: {e}"
