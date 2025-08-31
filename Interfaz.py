import streamlit as st
from main import procesar_cursos
from Funciones import colorear,borrar_excel
from Subir_A_Drive import subir_a_drive
#
from PIL import Image
from cryptography.fernet import Fernet
import json
import re
from decouple import config
import os # Importar os para verificar si el archivo existe

# Clave de cifrado segura desde variables de entorno (mejor para la nube)
clave = st.secrets["CLAVE_ENCRYPT"] # Se recomienda almacenar en Secret Manager
if not clave:
    st.error("❌ No se encontró la clave de cifrado. Configura CLAVE_ENCRYPT en las variables de entorno.")
    st.stop()

cipher_suite = Fernet(clave.encode())
ARCHIVO_JSON = "cursos_config.json"

def limpiar_rut(rut):
    """Convierte el RUT a un formato sin puntos y sin guion."""
    return re.sub(r"\D", "", rut)
def cargar_cursos():
    try:
        with open("cursos_config.json", "r") as f:
            data = json.load(f)
        
        cursos_actualizados = []
        for curso in data.get("cursos", []):
            # Si el curso tiene `rut` sin encriptar, lo convertimos
            if "rut" in curso and "password" in curso:
                curso["rut_encrypted"] = cipher_suite.encrypt(curso["rut"].encode()).decode()
                curso["password_encrypted"] = cipher_suite.encrypt(curso["password"].encode()).decode()
                del curso["rut"]
                del curso["password"]

            # Si el curso tiene `rut_sin_guion` sin encriptar, lo convertimos
            if "rut_sin_guion" in curso:
                curso["rut_sin_guion_encrypted"] = cipher_suite.encrypt(curso["rut_sin_guion"].encode()).decode()
                del curso["rut_sin_guion"]

            # Ahora desencriptamos para usarlo en la app
            curso["rut"] = cipher_suite.decrypt(curso["rut_encrypted"].encode()).decode()
            curso["rut_sin_guion"] = limpiar_rut(curso["rut"])
            curso["password"] = cipher_suite.decrypt(curso["password_encrypted"].encode()).decode()
            
            cursos_actualizados.append(curso)

        # Guardar cambios si se hicieron conversiones
        with open("cursos_config.json", "w") as f:
            json.dump({"cursos": cursos_actualizados}, f, indent=4)

        return cursos_actualizados

    except FileNotFoundError:
        st.error("Asegurese de tener cursos añadidos.")
        return []
    except Exception as e:
        st.error(f"Error al cargar cursos: {e}")
        return []

def guardar_cursos(cursos):
    """Guarda los cursos encriptando las credenciales."""
    cursos_encriptados = []
    for curso in cursos:
        cursos_encriptados.append({
            "nombre": curso["nombre"],
            "opcion_xpath": curso["opcion_xpath"],
            "rut_encrypted": cipher_suite.encrypt(curso["rut"].encode()).decode(),  # 🔐 Encriptado
            "rut_sin_guion_encrypted": cipher_suite.encrypt(limpiar_rut(curso["rut"]).encode()).decode(),  # 🔐 Encriptado
            "password_encrypted": cipher_suite.encrypt(curso["password"].encode()).decode(),  # 🔐 Encriptado
            "excel_porcentaje": f"{curso['nombre']}_porcentaje.xlsx",
            "dedicacion_file": f"{curso['nombre']}_dedication.xlsx",
            "calificaciones_file": f"{curso['nombre']} Calificaciones.xlsx",
            "resultado_final": f"{curso['nombre']} INFORME.xlsx"
        })

    with open(ARCHIVO_JSON, "w") as f:
        json.dump({"cursos": cursos_encriptados}, f, indent=4)

def agregar_curso(curso):
    """Añade un nuevo curso a la lista y lo guarda."""
    cursos = cargar_cursos()
    nuevo_curso = {
        "nombre": curso["nombre"],
        "opcion_xpath": curso["opcion_xpath"],
        "rut_encrypted": cipher_suite.encrypt(curso["rut"].encode()).decode(),  # 🔐 Encriptar RUT
        "rut_sin_guion_encrypted":cipher_suite.encrypt(limpiar_rut(curso["rut"]).encode()).decode(),
        "password_encrypted": cipher_suite.encrypt(curso["password"].encode()).decode(),  # 🔐 Encriptar contraseña
        "excel_porcentaje": curso["excel_porcentaje"],
        "dedicacion_file": curso["dedicacion_file"],
        "calificaciones_file": curso["calificaciones_file"],
        "resultado_final": curso["resultado_final"]
    }
    
    cursos.append(nuevo_curso)
    with open("cursos_config.json", "w") as f:
        json.dump({"cursos": cursos}, f, indent=4)

def eliminar_curso(index):
    """Elimina un curso según su índice."""
    cursos = cargar_cursos()
    if 0 <= index < len(cursos):
        cursos.pop(index)
        guardar_cursos(cursos)

st.set_page_config(page_title='Informes',page_icon="smile", layout="wide")
def main():
    st.title("Generador de informes de cursos SENCE")
    st.info("Se generará informes con los todos los datos requeridos excepto el RUT del alumno.")
    cursos = cargar_cursos()
    if cursos:
        st.subheader("📚 Cursos Guardados")
        curso_elegido = st.selectbox("Selecciona un curso del cual quieres generar informe:", [c["nombre"] for c in cursos])
        # Mostrar detalles
        curso_info = next((c for c in cursos if c["nombre"] == curso_elegido), None)
        if curso_info:
            #st.write(f"**XPath:** {curso_info['opcion_xpath']}")
            st.write(f"📂 **Codigo Curso:** {curso_info['nombre']}")
            #eliminar curso
            if st.button(f"❌ Eliminar {curso_info['nombre']}"):
                index = cursos.index(curso_info)
                eliminar_curso(index)
                st.success(f"Curso '{curso_info['nombre']}' eliminado.")
                st.rerun()
    else:
        st.warning("No hay cursos guardados. Agrega uno nuevo abajo.")

    #st.subheader("Añadir Nuevo Curso")
    with st.expander("➕ Añadir Nuevo Curso", expanded=False):
        with st.form("nuevo_curso",):
            nombre = st.text_input("📌 Nombre del curso (Código)")
            image=Image.open("xpath_image1.png")
            image2=Image.open("xpath_image.PNG")
            st.image(image,width=700)
            st.image(image2,width=700)
            xpath = st.text_input("🔗 XPath del curso (ejemplo arriba)")
            rut = st.text_input("👤 RUT con guión (ej:12345678-9)", type="password")
            password = st.text_input("🔑 Contraseña", type="password")

            if st.form_submit_button("Guardar curso"):
                if nombre and xpath and rut and password:
                    rut_sin_guion = limpiar_rut(rut)  # Generar RUT sin guion automáticamente
                    nuevo_curso = {
                        "nombre": nombre,
                        "opcion_xpath": xpath,
                        "rut": rut,
                        "rut_sin_guion": rut_sin_guion,  # Guardar RUT limpio en JSON
                        "password": password,
                        "excel_porcentaje": f"{nombre}_porcentaje.xlsx",
                        "dedicacion_file": f"{nombre}_dedication.xlsx",
                        "calificaciones_file": f"{nombre} Calificaciones.xlsx",
                        "resultado_final": f"{nombre} INFORME.xlsx"
                        }
                    agregar_curso(nuevo_curso)
                    st.success(f"✅ Curso '{nombre}' guardado correctamente.")
                    st.rerun()
                else:
                    st.error("⚠️ Todos los campos son obligatorios.")
            #st.rerun()  
    if cursos:
        if "df_final" not in st.session_state:
            st.session_state.df_final = None
        if curso_info:
            st.subheader("📄 Datos del curso seleccionado")
            st.write(f"📌 Código: {curso_info['nombre']}")
            st.write(f"🔗XPath: {curso_info['opcion_xpath']}")
            # Botón para generar informe
            if st.button("📊 Generar Informe"):
                st.session_state.df_final = procesar_cursos(
                    rut=curso_info["rut"],
                    rut_sin_guion=curso_info["rut_sin_guion"],
                    contrasena=curso_info["password"],
                    excel_porcentaje=curso_info["excel_porcentaje"],
                    opcion_xpath=curso_info["opcion_xpath"],
                    nombre_final=curso_info["resultado_final"]
                )

                # Manejo del resultado
                if isinstance(st.session_state.df_final, str):  
                    if st.session_state.df_final == "curso_terminado":
                        st.info("⚠️ Este curso ya terminó.")
                elif st.session_state.df_final is not None:
                    st.dataframe(st.session_state.df_final)
                    st.session_state.df_final_coloreado = colorear(st.session_state.df_final)
                    st.session_state.df_final_coloreado.to_excel(curso_info["resultado_final"], index=False)
                    st.success("Informe generado correctamente.")
                    borrar_excel(curso_info["excel_porcentaje"])
                else:
                    st.error("❌ No se pudo generar el informe. Revisa la consola para ver los errores.")

            # FIX: Lógica de subida a Drive corregida
            if st.button("📤 Subir informe a Drive"):
                nombre_informe_final = curso_info["resultado_final"]
                # 1. Verificar que el informe final exista antes de intentar subirlo
                if os.path.exists(nombre_informe_final):
                    if subir_a_drive(nombre_informe_final):
                        st.success(f"✅ Informe '{nombre_informe_final}' subido a Drive correctamente.")
                    else:
                        st.error("❌ Error al subir el informe a Drive.")
                else:
                    st.warning(f"⚠️ No se encontró el informe '{nombre_informe_final}'. Por favor, genéralo primero.")

if __name__=='__main__':

    main()

