from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

def subir_a_drive(excel_name):
    SERVICE_ACCOUNT_FILE= "credenciales.json"
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build("drive", "v3", credentials=credentials)
    file_metadata = {
        "name": excel_name,
        "parents": ["1sNvSSpg7Vy0YNRbsgsilgExJ01q6bqaX"]  # ID de la carpeta de Drive
    }
    media = MediaFileUpload(excel_name, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"Archivo subido con éxito: {excel_name}")
    return True
