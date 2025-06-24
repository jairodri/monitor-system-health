import yaml
from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import cx_Oracle
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import win32com.client

    
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
    
def generate_html_report(results: list[dict]) -> str:
    """
    Genera un reporte HTML a partir de una lista de resultados de verificación.
    """
    styles = """
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; color: #333; }
        h1 { color: #2c3e50; }
        table { border-collapse: collapse; width: 100%; max-width: 800px; box-shadow: 0 2px 3px #ccc; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #3498db; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .status-ok { color: #27ae60; font-weight: bold; }
        .status-fail { color: #c0392b; font-weight: bold; }
        .message { font-size: 0.9em; color: #7f8c8d; }
    </style>
    """
    rows_html = ""
    for result in results:
        web_status, web_message = result['web_status']
        db_status, db_message = result['db_tasks']
        web_status_html = f"<span class='{'status-ok' if web_status else 'status-fail'}'>{'ÉXITO' if web_status else 'FALLO'}</span>"
        db_status_html = f"<span class='{'status-ok' if db_status else 'status-fail'}'>{'ÉXITO' if db_status else 'FALLO'}</span>"
        rows_html += f"""
        <tr>
            <td>{result['name']}</td>
            <td>{web_status_html}<div class='message'>{web_message}</div></td>
            <td>{db_status_html}<div class='message'>{db_message}</div></td>
        </tr>
        """
    html_template = f"""
    <!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Reporte Operativo</title>{styles}</head>
    <body>
        <h1>Reporte Operativo de Sistemas</h1>
        <p>Fecha del reporte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <table><thead><tr><th>Sistema</th><th>Estado Web</th><th>Estado Base de Datos</th></tr></thead>
        <tbody>{rows_html}</tbody></table>
    </body></html>
    """
    return html_template

def send_email(subject: str, body: str, recipients: list[str], smtp_config: dict):
    """
    Envía un correo electrónico HTML a través de un servidor SMTP con autenticación.
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    smtp_host = smtp_config['host']
    smtp_port = int(smtp_config['port'])
    smtp_user = smtp_config['user']
    smtp_password = smtp_config.get('password', None)
    print(f'smtp_host: {smtp_host}, smtp_port: {smtp_port}, smtp_user: {smtp_user}, smtp_password: {smtp_password}')


    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = ", ".join(recipients)
    msg.attach(MIMEText(body, 'html', 'utf-8'))  # Especifica codificación

    server = None
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        print(f'server: {server}')
        server.ehlo()
        if smtp_password:  # Solo intenta autenticación si hay contraseña
            server.starttls()
            print("INFO: Autenticación SMTP iniciada.")
            server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipients, msg.as_string())
        print(f"Correo de reporte enviado exitosamente a: {', '.join(recipients)}")
    except Exception as e:
        print(f"ERROR CRÍTICO: No se pudo enviar el correo. Detalles: {e}")
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass

def generate_outlook_email(subject: str, body: str, recipients: list[str]):
    """
    Genera un correo en Outlook con el asunto, destinatarios y cuerpo HTML proporcionados.
    El correo se abre en modo edición para que el usuario lo revise y lo envíe manualmente.
    """
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.Subject = subject
        mail.To = "; ".join(recipients)
        mail.HTMLBody = body
        mail.Display()  # Abre el correo en modo edición
        print("Correo generado en Outlook. Revísalo y pulsa Enviar.")
    except Exception as e:
        print(f"ERROR: No se pudo generar el correo en Outlook. Detalles: {e}")
    