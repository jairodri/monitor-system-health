import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# def check_web_ui(url: str, user: str, password: str, selectors: dict, headless: bool = True) -> tuple[bool, str]:
#     """
#     Realiza una verificación completa de la interfaz web: navegación, login y logout.

#     Args:
#         url (str): La URL de la página de login.
#         user (str): El nombre de usuario para la conexión.
#         password (str): La contraseña para la conexión.
#         selectors (dict): Un diccionario con los selectores CSS para interactuar con la página.
#                           Debe contener: 'user_input', 'pass_input', 'submit_button',
#                           'success_indicator', y 'logout_button'.
#         headless (bool, optional): Si es True, el navegador se ejecuta sin interfaz gráfica. 
#                                    Defaults to True.

#     Returns:
#         tuple[bool, str]: Una tupla donde el primer elemento es un booleano (True para éxito,
#                           False para error) y el segundo es un mensaje descriptivo del resultado.
#     """
#     try:
#         with sync_playwright() as p:
#             # 1. Iniciar el navegador (Chromium es una excelente opción por su compatibilidad)
#             browser = p.chromium.launch(headless=headless, args=["--disable-gpu"])
#             context = browser.new_context(ignore_https_errors=True)
#             page = context.new_page()

#             # 2. Navegar a la URL
#             print(f"INFO: Navegando a la URL: {url}")
#             page.goto(url, wait_until='domcontentloaded', timeout=20000) # 20 segundos de timeout
#             print("INFO: Página de login cargada.")

#             # 3. Introducir credenciales y hacer login
#             print("INFO: Introduciendo credenciales...")
#             # Rellenar el campo de usuario
#             page.locator(selectors['user_input']).fill(user)
#             # Rellenar el campo de contraseña
#             page.locator(selectors['pass_input']).fill(password)
            
#             print("INFO: Enviando formulario de login...")
#             # Hacer clic en el botón de submit
#             page.locator(selectors['submit_button']).click()

#             # 4. Comprobar que la conexión es correcta
#             # Esperamos a que aparezca un elemento que solo es visible tras un login exitoso.
#             print("INFO: Verificando indicador de éxito post-login...")
#             success_element = page.locator(selectors['success_indicator'])
#             success_element.wait_for(state='visible', timeout=20000) # 20 seg de timeout
#             print("INFO: Login verificado correctamente.")

#             # 5. Hacer logout
#             print("INFO: Realizando logout...")
#             page.locator(selectors['logout_button']).click()

#             # Opcional: Verificar que hemos vuelto a la página de login
#             logout_success_element = page.locator(selectors['user_input'])
#             logout_success_element.wait_for(state='visible', timeout=10000)
#             print("INFO: Logout verificado correctamente.")
            
#             # 6. Cerrar el navegador
#             browser.close()
            
#             return True, "Login y logout realizados correctamente."

#     except PlaywrightTimeoutError as e:
#         error_message = f"Timeout esperando un elemento o navegación. ¿La URL es correcta o la página es muy lenta? Detalles: {e}"
#         print(f"ERROR: {error_message}")
#         # Aquí se podría añadir una captura de pantalla para depuración
#         # page.screenshot(path=f"error_screenshot_{int(time.time())}.png")
#         return False, f"ERROR: {error_message}"
#     except Exception as e:
#         error_message = f"Ha ocurrido un error inesperado. ¿Son correctos los selectores CSS? Detalles: {e}"
#         print(f"ERROR: {error_message}")
#         return False, f"ERROR: {error_message}"

def check_web_ui(url: str, user: str, password: str, selectors: dict, headless: bool = True) -> tuple[bool, str]:
    """
    Realiza una verificación de la interfaz web: navegación, login (si aplica) y logout.

    Si user y password están vacíos, se asume que no hay autenticación y solo se hace clic en un botón de OK.

    Args:
        url (str): La URL de la página de login o acceso.
        user (str): El nombre de usuario para la conexión (vacío si no hay login).
        password (str): La contraseña para la conexión (vacío si no hay login).
        selectors (dict): Diccionario con los selectores CSS necesarios.
        headless (bool): Si es True, el navegador se ejecuta sin interfaz gráfica.

    Returns:
        tuple[bool, str]: (True/False, mensaje)
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless, args=["--disable-gpu"])
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            print(f"INFO: Navegando a la URL: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=20000)
            print("INFO: Página inicial cargada.")

            if user or password:
                # Flujo con autenticación
                print("INFO: Introduciendo credenciales...")
                page.locator(selectors['user_input']).fill(user)
                page.locator(selectors['pass_input']).fill(password)
                print("INFO: Enviando formulario de login...")
                page.locator(selectors['submit_button']).click()
                print("INFO: Verificando indicador de éxito post-login...")
                page.locator(selectors['success_indicator']).wait_for(state='visible', timeout=20000)
                print("INFO: Login verificado correctamente.")
            else:
                # Flujo sin autenticación: solo botón OK
                print("INFO: No se requiere autenticación. Buscando botón OK...")
                page.locator(selectors['ok_button']).click()
                print("INFO: Botón OK pulsado. Esperando página principal...")
                page.locator(selectors['success_indicator']).wait_for(state='visible', timeout=20000)
                print("INFO: Página principal cargada tras OK.")

            # Logout (en ambos casos)
            print("INFO: Realizando logout...")
            page.locator(selectors['logout_button']).click()
            # Opcional: Verificar que hemos vuelto a la página de inicio/login
            if user or password:
                page.locator(selectors['user_input']).wait_for(state='visible', timeout=10000)
            else:
                # Si no hay login, podrías buscar el botón OK de nuevo o algún otro indicador
                page.locator(selectors['ok_button']).wait_for(state='visible', timeout=10000)
            print("INFO: Logout verificado correctamente.")

            browser.close()
            return True, "Verificación web completada correctamente."

    except PlaywrightTimeoutError as e:
        error_message = f"Timeout esperando un elemento o navegación. ¿La URL es correcta o la página es muy lenta? Detalles: {e}"
        print(f"ERROR: {error_message}")
        return False, f"ERROR: {error_message}"
    except Exception as e:
        error_message = f"Ha ocurrido un error inesperado. ¿Son correctos los selectores CSS? Detalles: {e}"
        print(f"ERROR: {error_message}")
        return False, f"ERROR: {error_message}"
    

