from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

def subir_a_drive(excel_name):
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    # Obtiene el diccionario de credenciales desde st.secrets
    creds_dict = st.secrets["google_credentials"]
    credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build("drive", "v3", credentials=credentials)
    file_metadata = {
        "name": excel_name,
        "parents": ["1sNvSSpg7Vy0YNRbsgsilgExJ01q6bqaX"]  # ID de la carpeta de Drive
    }
    media = MediaFileUpload(excel_name, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"Archivo subido con éxito: {excel_name}")
    return True

