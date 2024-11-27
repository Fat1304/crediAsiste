import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Definir el alcance para Google Sheets y Google Drive
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Ruta al archivo JSON de credenciales
CREDENTIALS_FILE = '/Users/pauloueda/Desktop/crediasisteCredenciales.json'

# Autenticarse con la cuenta de servicio
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES)
client = gspread.authorize(credentials)

# Abrir el Google Sheets (cambia "Nombre de tu Google Sheets" por el nombre real del archivo)
spreadsheet = client.open("GestionesProbabilidades")  # Nombre del archivo Google Sheets
sheet = spreadsheet.sheet1  # Selecciona la primera hoja

# Leer los datos
data = sheet.get_all_records()
print("Datos del Google Sheets:")
print(data)

# Opcional: Escribir en el Google Sheets
sheet.append_row(["Ejemplo", "Nuevo Dato", 123])  # Añade una nueva fila
