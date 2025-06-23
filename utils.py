import yaml
from dotenv import dotenv_values

    
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
