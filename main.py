from web_checker_module import check_web_ui
from database_checker_module import check_database
from utils import load_yaml_config, load_secrets, generate_html_report, send_email, generate_outlook_email

   
def main():
    """
    Punto de entrada principal para el monitor de salud del sistema.
    """
    print("========================================")
    print("== INICIANDO MONITOR DE SALUD SISTEMA ==")
    print("========================================")

    # 1. Cargar la configuración desde el fichero YAML
    config = load_yaml_config("config.yaml")
    if not config:
        print("Error crítico: No se pudo cargar la configuración. Abortando.")
        return
    
    # 2. Cargar los secretos desde el fichero .env
    secrets = load_secrets('.env')
    if not secrets:
        print("Error crítico: Faltan secretos en el fichero .env. Abortando.")
        return

    all_results = []

    # 3. Iterar sobre cada sistema
    for system in config['systems_to_check']:
        if not system['enabled']:
            continue

        system_name = system['name']
        system_description = system['description']
        print(f"\n== Verificando sistema: {system_name} ==")
        
        # 4. Ejecutar verificación web
        web_password_key = f"{system_name.upper()}_WEB_PASSWORD"
        try:
            web_status, web_message = check_web_ui(
                url=system['web']['url'],
                user=system['web']['user'],
                password=secrets[web_password_key],
                selectors=system['web']['selectors'],
                headless=True
            )
        except Exception as e:
            web_status = False 
            web_message = f"ERROR: {e}"

        # # 5. Ejecutar verificación de base de datos
        db_password_key = f"{system_name.upper()}_DB_PASSWORD"
        db_config = {
            'host': system['database']['host'],
            'port': system['database']['port'],
            'service_name': system['database']['db_name'],
            'username': system['database']['user'],
            'password': secrets[db_password_key]
        }
        try:
            db_status, db_message = check_database(
                db_type=system['database']['db_type'],
                db_config=db_config
            ) 
        except Exception as e:
            db_status = False
            db_message = f"ERROR: {e}"
            
        all_results.append({
            "name": system_description,
            "web_status": (web_status, web_message),
            "db_tasks": (db_status, db_message) 
        })
        print(f"Resultados para {system_name}:")
        print(f"  Web: {web_status} - {web_message}")
        print(f"  DB: {db_status} - {db_message}")

    # # 6. Generar y enviar el reporte
    email_body = generate_html_report(all_results)
    smtp_config = {
        'host': config['smtp_server'],
        'port': config['smtp_port'],
        'user': config['smtp_user'],
        'password': secrets['SMTP_PASSWORD']
    }

    # send_email(
    #     subject="Reporte Operativo de Sistemas",
    #     body=email_body,
    #     recipients=config['email_recipients'],
    #     smtp_config=smtp_config
    # )
    generate_outlook_email(
        subject="Reporte Operativo de Sistemas",
        body=email_body,
        recipients=config['email_recipients']
    )

if __name__ == "__main__":
    main()
    print("Monitorización de sistemas completada. Revisa tu correo para el reporte.")   
