import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread

# Configurar las credenciales y la conexión con Google Sheets
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentialsFile = '/Users/pauloueda/Desktop/crediasisteCredenciales.json'

# Crear conexión con Google Sheets
credentials = Credentials.from_service_account_file(credentialsFile, scopes=scopes)
client = gspread.authorize(credentials)

# Abrir el Google Sheets
spreadsheet = client.open("GestionesProbabilidades")  # Cambiar por el nombre real
sheet = spreadsheet.sheet1  # Primera hoja

# Cargar datos como DataFrame
data = pd.DataFrame(sheet.get_all_records())

if 'pagina' not in st.session_state:
    st.session_state['pagina'] = 'inicio'

# Asignar clientes a gestores
data['usuarioAsignado'] = ''  # Crear columna si no existe
data.loc[:124, 'usuarioAsignado'] = 'gestorLlamadas'
data.loc[125:134, 'usuarioAsignado'] = 'gestorPuertaPuerta'

# Actualizar en Google Sheets
# Crear una lista con las filas completas actualizadas
actualizaciones = data[['usuarioAsignado']].values.tolist()

# Actualizar toda la columna de 'usuarioAsignado' en Google Sheets
sheet.update(range_name='BK2:BK', values=actualizaciones)

# Funciones para las pantallas
def mostrarPantallaAdministrador():
    st.title("Panel de Administrador")
    st.write("Clientes asignados a los gestores:")

    # Mostrar todos los datos
    st.dataframe(data)

    # Reasignar clientes
    clienteSeleccionado = st.selectbox("Selecciona un cliente para reasignar:", data["Nombre"].unique())
    nuevoGestor = st.selectbox("Selecciona el nuevo gestor:", ["gestorLlamadas", "gestorPuertaPuerta"])
    
    if st.button("Reasignar Cliente"):
        indexCliente = data[data["Nombre"] == clienteSeleccionado].index[0]
        data.at[indexCliente, "usuarioAsignado"] = nuevoGestor
        sheet.update_cell(indexCliente + 2, data.columns.get_loc("usuarioAsignado") + 1, nuevoGestor)
        st.success(f"Cliente {clienteSeleccionado} reasignado a {nuevoGestor}.")

def mostrarPantallaGestor(usuario):
    st.title(f"Panel de Gestor: {usuario}")
    st.write("Clientes asignados:")

    # Filtrar clientes por usuario actual
    clientesAsignados = data[data["usuarioAsignado"] == usuario]
    st.dataframe(clientesAsignados)

    clienteSeleccionado = st.selectbox("Selecciona un cliente para gestionar:", clientesAsignados["Nombre"].unique())
    if st.button("Registrar Nueva Interacción"):
        st.session_state['clienteSeleccionado'] = clienteSeleccionado
        st.session_state['pagina'] = 'interacciones'
        st.experimental_rerun()

def mostrarInteraccionesCliente():
    cliente = st.session_state['clienteSeleccionado']
    st.title(f"Registrar Interacción para {cliente}")

    with st.form("formInteraccion"):
        tipoGestion = st.selectbox("Tipo de Gestión", ["Llamada", "Visita"])
        resultado = st.selectbox("Resultado", ["Promesa de Pago", "Sin Respuesta", "Negativa"])
        notas = st.text_area("Notas Adicionales")
        submit = st.form_submit_button("Guardar")

        if submit:
            st.success(f"Interacción guardada para {cliente}.")
            st.session_state['pagina'] = 'gestor'
            st.experimental_rerun()

# Navegación
if 'pagina' not in st.session_state:
    st.session_state['pagina'] = 'inicio'

if st.session_state['pagina'] == 'inicio':
    usuario = st.selectbox("Selecciona tu rol:", ["Administrador", "gestorLlamadas", "gestorPuertaPuerta"])
    if st.button("Iniciar Sesión"):
        st.session_state['usuario'] = usuario
        st.session_state['pagina'] = 'administrador' if usuario == "Administrador" else 'gestor'
        st.experimental_rerun()

elif st.session_state['pagina'] == 'administrador':
    mostrarPantallaAdministrador()

elif st.session_state['pagina'] == 'gestor':
    mostrarPantallaGestor(st.session_state['usuario'])

elif st.session_state['pagina'] == 'interacciones':
    mostrarInteraccionesCliente()