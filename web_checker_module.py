import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def check_web_ui(url: str, user: str, password: str, selectors: dict, headless: bool = True) -> tuple[bool, str]:
    """
    Realiza una verificación completa de la interfaz web: navegación, login y logout.

    Args:
        url (str): La URL de la página de login.
        user (str): El nombre de usuario para la conexión.
        password (str): La contraseña para la conexión.
        selectors (dict): Un diccionario con los selectores CSS para interactuar con la página.
                          Debe contener: 'user_input', 'pass_input', 'submit_button',
                          'success_indicator', y 'logout_button'.
        headless (bool, optional): Si es True, el navegador se ejecuta sin interfaz gráfica. 
                                   Defaults to True.

    Returns:
        tuple[bool, str]: Una tupla donde el primer elemento es un booleano (True para éxito,
                          False para error) y el segundo es un mensaje descriptivo del resultado.
    """
    try:
        with sync_playwright() as p:
            # 1. Iniciar el navegador (Chromium es una excelente opción por su compatibilidad)
            browser = p.chromium.launch(headless=headless, args=["--disable-gpu"])
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            # 2. Navegar a la URL
            print(f"INFO: Navegando a la URL: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=20000) # 20 segundos de timeout
            print("INFO: Página de login cargada.")

            # 3. Introducir credenciales y hacer login
            print("INFO: Introduciendo credenciales...")
            # Rellenar el campo de usuario
            page.locator(selectors['user_input']).fill(user)
            # Rellenar el campo de contraseña
            page.locator(selectors['pass_input']).fill(password)
            
            print("INFO: Enviando formulario de login...")
            # Hacer clic en el botón de submit
            page.locator(selectors['submit_button']).click()

            # 4. Comprobar que la conexión es correcta
            # Esperamos a que aparezca un elemento que solo es visible tras un login exitoso.
            print("INFO: Verificando indicador de éxito post-login...")
            success_element = page.locator(selectors['success_indicator'])
            success_element.wait_for(state='visible', timeout=20000) # 20 seg de timeout
            print("INFO: Login verificado correctamente.")

            # 5. Hacer logout
            print("INFO: Realizando logout...")
            page.locator(selectors['logout_button']).click()

            # Opcional: Verificar que hemos vuelto a la página de login
            logout_success_element = page.locator(selectors['user_input'])
            logout_success_element.wait_for(state='visible', timeout=10000)
            print("INFO: Logout verificado correctamente.")
            
            # 6. Cerrar el navegador
            browser.close()
            
            return True, "OK: Login y logout realizados correctamente."

    except PlaywrightTimeoutError as e:
        error_message = f"Timeout esperando un elemento o navegación. ¿La URL es correcta o la página es muy lenta? Detalles: {e}"
        print(f"ERROR: {error_message}")
        # Aquí se podría añadir una captura de pantalla para depuración
        # page.screenshot(path=f"error_screenshot_{int(time.time())}.png")
        return False, f"ERROR: {error_message}"
    except Exception as e:
        error_message = f"Ha ocurrido un error inesperado. ¿Son correctos los selectores CSS? Detalles: {e}"
        print(f"ERROR: {error_message}")
        return False, f"ERROR: {error_message}"


# --- Bloque de Prueba ---
# Este código solo se ejecuta cuando corres el script directamente (python web_checker_module.py)
if __name__ == "__main__":
    print("=====================================================")
    print("== INICIANDO PRUEBA DEL MÓDULO DE VERIFICACIÓN WEB ==")
    print("=====================================================")

    # Configuración para el sistema de prueba (un sitio web público)
    # En el sistema final, esta información vendrá del fichero config.yaml
    test_system_config = {
        "url": "https://the-internet.herokuapp.com/login",
        "user": "tomsmith",
        "password": "SuperSecretPassword!",
        "selectors": {
            "user_input": "input#username",
            "pass_input": "input#password",
            "submit_button": "button[type='submit']",
            "success_indicator": "div#flash.success", # Un div con id 'flash' y clase 'success'
            "logout_button": "a[href='/logout']"
        }
    }

    # Para ver la ejecución en una ventana, cambia headless a False
    # Esto es muy útil para depurar y encontrar los selectores correctos.
    is_headless = True 
    print(f"\nEjecutando en modo {'headless (sin ventana)' if is_headless else 'con ventana'}.\n")

    # Llamamos a la función principal con la configuración de prueba
    success, message = check_web_ui(
        url=test_system_config["url"],
        user=test_system_config["user"],
        password=test_system_config["password"],
        selectors=test_system_config["selectors"],
        headless=is_headless
    )

    print("\n-------------------")
    print("--- RESULTADO FINAL ---")
    print(f"Éxito: {success}")
    print(f"Mensaje: {message}")
    print("-------------------\n")