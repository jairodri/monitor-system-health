import yaml
from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import cx_Oracle
    
def load_yaml_config(file_path: str) -> dict:
    """
    Carga un fichero de configuración YAML.

    Args:
        file_path (str): La ruta al fichero de configuración.

    Returns:
        dict: Un diccionario con la configuración o None si hay un error.
    """
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"ERROR: El fichero de configuración '{file_path}' no fue encontrado.")
        return None
    except yaml.YAMLError as e:
        print(f"ERROR: Error al procesar el fichero YAML '{file_path}': {e}")
        return None

def load_secrets(file_path: str = ".env") -> dict:
    """
    Carga todas las variables de un fichero .env en un diccionario.

    Args:
        file_path (str): La ruta al fichero .env.

    Returns:
        dict: Un diccionario con las variables de entorno del fichero.
    """
    secrets = dotenv_values(file_path)
    return secrets

def connect_to_oracle(host:str, port:int, service_name:str, username:str, password:str):
    """
    Function to connect to an Oracle database using SQLAlchemy and cx_Oracle.
    From version 8 onwards, cx_Oracle has been renamed to oracledb, though cx_Oracle is still functional in earlier versions.

    Parameters:
    - host: The address of the database server.
    - port: The port where the database server is listening.
    - service_name: The service name of the database.
    - username: The database user's name.
    - password: The password for the database user.

    Returns:
    - engine: SQLAlchemy Engine object if the connection is successful.
    - None: If an error occurs during the connection.
    """
    # Create the connection string in the format required by SQLAlchemy and cx_Oracle
    connection_string = f'oracle+cx_oracle://{username}:{password}@{host}:{port}/?service_name={service_name}'
    
    try:
        engine = create_engine(connection_string)
        return engine
    except SQLAlchemyError as e:
        print(f"Error connecting to the database: {e}")
        return None
    