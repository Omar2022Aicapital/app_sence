from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from decouple import config
from Funciones import dedicacion,unir_porcentajeYhoras,unir_notas,procesamiento_notas

# FIX: La lista de cursos hardcodeada ha sido eliminada.
# La configuración de los cursos ahora se maneja exclusivamente
# desde la interfaz de Streamlit y el archivo 'cursos_config.json'.

# Configuración del navegador
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# Para evitar problemas con la detección de automatización
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

service = Service(ChromeDriverManager().install())

def procesar_cursos(rut,rut_sin_guion,contrasena, excel_porcentaje,opcion_xpath,nombre_final):
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    url = "https://auladigital.sence.cl/login/index.php"
    driver.get(url)
    wait = WebDriverWait(driver, 20) # Aumentado el tiempo de espera para más fiabilidad
    resultado=[]
    datos_dedi = []
    nombres_columnas=[]
    datos_cali = []
    try:
        # --- LOGIN ---
        rut_input = wait.until(EC.element_to_be_clickable((By.ID, "rut")))
        rut_input.send_keys(rut)
        rut_input.send_keys(Keys.ENTER) 
        
        curso_clic = wait.until(EC.element_to_be_clickable((By.ID, "curso")))
        curso_clic.click()
        
        curso_opcion = wait.until(EC.element_to_be_clickable((By.XPATH, opcion_xpath)))
        curso_opcion.click()

        wait.until(EC.element_to_be_clickable((By.ID, "btnLogin"))).click()
        
        clave_name = wait.until(EC.element_to_be_clickable((By.ID, "uname")))
        clave_name.send_keys(rut_sin_guion)
        
        clave_ps = driver.find_element(By.ID, "pword")
        clave_ps.send_keys(contrasena)
        
        driver.find_element(By.ID, "login-submit").click()
        
        ########### VISTA PORCENTAJE AVANCE #####################################################################################
        
        # FIX: Selector robusto para el botón de vista de progreso. Busca un formulario que apunte a la URL de progreso.
        botonVista_selector = (By.CSS_SELECTOR, "form[action*='report/progress'] button")
        botonVista = wait.until(EC.element_to_be_clickable(botonVista_selector))
        botonVista.click()
        
        try:
            # FIX: Selector robusto para detectar si el curso ha terminado.
            terminado_selector = (By.XPATH, "//h2[contains(text(), 'Este curso ha finalizado')]")
            terminado = WebDriverWait(driver, 5).until(EC.presence_of_element_located(terminado_selector))
            print("El curso ha terminado.")
            return "curso_terminado"
        except Exception:
            print("El curso sigue operativo.")

        wait.until(EC.element_to_be_clickable((By.ID,'showall'))).click()
        
        tbody = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.flexible.overviewTable tbody")))
        filas = tbody.find_elements(By.TAG_NAME, "tr")
        for fila in filas:
            columnas=fila.find_elements(By.TAG_NAME, "td")
            datos=[col.text for col in columnas]
            if datos and datos[2]: # Asegurarse de que la fila no esté vacía
                resultado.append({
                        "Nombre estudiante": datos[2],
                        "Porcentaje Progreso": datos[-1]
                        })
        df_resultado = pd.DataFrame(resultado)
        df_resultado.to_excel(excel_porcentaje, index=False)
        print("✅ Porcentaje LISTO!")

        # --- NAVEGACIÓN HACIA ATRÁS ---
        driver.back()
        driver.back()

        ############## HERRAMIENTAS DE DEDICACION #############################################################################
        
        # FIX: Selector robusto para el botón de dedicación.
        dedicacion_selector = (By.CSS_SELECTOR, "form[action*='report/dedication'] button")
        boton_Dedicacion_curso = wait.until(EC.element_to_be_clickable(dedicacion_selector))
        boton_Dedicacion_curso.click()

        tabla_dedicacion_selector = (By.CSS_SELECTOR, "table.table-dedication tbody")
        tabla = wait.until(EC.presence_of_element_located(tabla_dedicacion_selector))
        filas = tabla.find_elements(By.TAG_NAME, "tr")
        for fila in filas:
            columnas = fila.find_elements(By.TAG_NAME, "td")
            if columnas:
                datos_fila = [col.text for col in columnas]
                datos_dedi.append(datos_fila)
        print(f"✅ Dedicación LISTO!")
        
        # --- CALIFICACIONES ---
        calificaciones_selector = (By.CSS_SELECTOR, "a[href*='/grade/report/user']")
        wait.until(EC.element_to_be_clickable(calificaciones_selector)).click()

        tabla2 = wait.until(EC.presence_of_element_located((By.ID, "user-grades")))
        encabezados = tabla2.find_elements(By.CSS_SELECTOR, "tr.heading th")
        nombres_columnas.extend(th.text for th in encabezados)

        filas = tabla2.find_elements(By.CSS_SELECTOR, "tbody tr:not(.heading)")
        for fila in filas:
            nombre = fila.find_element(By.TAG_NAME, "th").text
            if not nombre: continue # Omitir filas sin nombre

            columnas = fila.find_elements(By.TAG_NAME, "td")
            datos_fila = [nombre] + [col.text for col in columnas]
            datos_cali.append(datos_fila)
        print("✅ Calificaciones LISTO!")

    except Exception as e:
        print(f"❌ Ocurrió un error durante la automatización: {e}")
        driver.save_screenshot("error_screenshot.png") # Guarda una captura para depuración
        return None # Devuelve None para indicar que falló
    finally:
        # --- CERRAR SESIÓN ---
        try:
            # FIX: Selector robusto para el menú de usuario y el botón de salir.
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'userbutton'))).click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'logout.php')]"))).click()
            print("Sesión cerrada correctamente.")
        except Exception as e:
            print(f"No se pudo cerrar sesión de forma limpia: {e}")
        driver.quit()

    df_cali = pd.DataFrame(datos_cali, columns=nombres_columnas)
    df_dedi = pd.DataFrame(datos_dedi, columns=["Imagen", "Nombre", "Apellido(s)", "Grupo", "Dedicación al curso", "Conexiones por día"])

    df_final=ejecutar_flujo(df_dedi, excel_porcentaje, df_cali, nombre_final)
    return df_final