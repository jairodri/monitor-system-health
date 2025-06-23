from web_checker_module import check_web_ui
from utils import load_yaml_config, load_secrets

   
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
        password_key = f"{system_name.upper()}_WEB_PASSWORD"
        
        # 4. Ejecutar verificación web
        try:
            web_status, message = check_web_ui(
                url=system['web']['url'],
                user=system['web']['user'],
                password=secrets[password_key],
                selectors=system['web']['selectors'],
                headless=True
            )
        except Exception as e:
            web_status = f"ERROR: {e}"

        # # 5. Ejecutar verificación de base de datos
        # try:
        #     db_status = check_database(system['database']) # Devuelve el número de tareas o "ERROR: [motivo]"
        # except Exception as e:
        #     db_status = f"ERROR: {e}"
            
        all_results.append({
            "name": system_name,
            "web_status": web_status,
            "db_tasks": web_status # Aquí deberías agregar la lógica para obtener el número de tareas de la base de datos
        })

    # # 6. Generar y enviar el reporte
    # email_body = generate_html_report(all_results)
    # send_email(
    #     subject="Reporte Operativo de Sistemas",
    #     body=email_body,
    #     recipients=config['email_recipients'],
    #     smtp_config=config['smtp_server']
    # )

if __name__ == "__main__":
    main()
    print("Monitorización de sistemas completada. Revisa tu correo para el reporte.")   
