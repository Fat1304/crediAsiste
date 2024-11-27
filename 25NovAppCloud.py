import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json

# Configuración de la conexión a Google Sheets
def conectarGoogleSheets():
    try:
        # Rango de acceso para Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Leer credenciales desde st.secrets
        credentials_dict = json.loads(st.secrets["credentials"])
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        # Autorización y conexión con Google Sheets
        client = gspread.authorize(credentials)
        sheet = client.open_by_url(st.secrets["spreadsheet"]).sheet1
        return sheet
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return None

# Leer datos de Google Sheets
def leerDatos(sheet):
    try:
        data = sheet.get_all_records()
        return data
    except Exception as e:
        st.error(f"Error al leer datos: {e}")
        return []

# Actualizar una celda específica en Google Sheets
def actualizarGoogleSheets(sheet, fila, columna, valor):
    try:
        sheet.update_cell(fila, columna, valor)
        st.success(f"Celda actualizada en fila {fila}, columna {columna}.")
    except Exception as e:
        st.error(f"Error al actualizar Google Sheets: {e}")

# Flujo principal
def flujoPantallas():
    st.title("Conexión a Google Sheets")
    sheet = conectarGoogleSheets()
    if sheet:
        st.success("Conexión exitosa a Google Sheets")
        data = leerDatos(sheet)
        if data:
            st.write("Datos en Google Sheets:")
            st.write(data)
        else:
            st.info("No hay datos disponibles para mostrar.")

# Ejecutar flujo
flujoPantallas()
