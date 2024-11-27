import streamlit as st
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Configuración de la API de Google Sheets
def conectarGoogleSheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("crediasisteCredenciales.json", scope)
    client = gspread.authorize(credentials)
    sheet = client.open("DemoDimi").sheet1
    return sheet

# Leer datos del Google Sheets
def leerDatos(sheet):
    data = sheet.get_all_records()
    return data

# Actualizar una celda específica en Google Sheets
def actualizarGoogleSheets(sheet, fila, columna, valor):
    try:
        sheet.update_cell(fila, columna, valor)
    except Exception as e:
        st.error(f"Error al actualizar Google Sheets: {e}")

# Obtener índice de una columna basada en su nombre
def obtenerIndiceColumna(sheet, nombre_columna):
    cabeceras = sheet.row_values(1)
    if nombre_columna in cabeceras:
        return cabeceras.index(nombre_columna) + 1
    else:
        raise ValueError(f"La columna '{nombre_columna}' no existe en la hoja.")

# Convertir probabilidad a nivel
def convertirProbabilidad(probabilidad):
    if probabilidad <= 0.30:
        return "Bajo"
    elif probabilidad <= 0.70:
        return "Medio"
    else:
        return "Alto"

# Pantalla de inicio de sesión
def pantallaInicioSesion(sheet):
    st.title("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        data = leerDatos(sheet)
        gestores = {fila["Gestor"]: fila for fila in data if fila["Gestor"]}

        if username == "admin" and password == "admin":
            st.session_state["role"] = "admin"
            st.session_state["pantalla_actual"] = "resumen_admin"
            st.experimental_rerun()
        elif username in gestores and password == "gestor":
            st.session_state["role"] = username
            st.session_state["clientes"] = [
                fila for fila in data if fila.get("Gestor", "").strip().lower() == username.lower()
            ]
            st.session_state["pantalla_actual"] = "lista_clientes"
            st.experimental_rerun()
        else:
            st.error("Credenciales incorrectas")

# Pantalla de resumen del administrador
def pantallaResumenAdministrador(sheet):
    st.title("Resumen General - Administrador")
    data = leerDatos(sheet)

    total_clientes = len(data)
    gestionados = sum(1 for fila in data if fila["Gestionado"] == 1)
    porcentaje = (gestionados / total_clientes) * 100
    monto_total_deuda = sum(float(fila.get("Deuda", 0)) for fila in data)

    st.metric("Clientes Gestionados", f"{gestionados} de {total_clientes}", f"{porcentaje:.2f}%")
    st.metric("Monto Total de la Deuda", f"${monto_total_deuda:,.2f}")

    st.header("Lista de Gestores")
    gestores = set(fila["Gestor"] for fila in data if fila["Gestor"])
    for gestor in gestores:
        if st.button(f"Ver {gestor}"):
            st.session_state["clientes"] = [fila for fila in data if fila["Gestor"] == gestor]
            st.session_state["pantalla_actual"] = "lista_clientes"
            st.experimental_rerun()

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "inicio"
        st.experimental_rerun()

# Mostrar cliente en lista
def mostrarCliente(cliente):
    prob = convertirProbabilidad(cliente["Probabilidad Cuenta Deteriorada"])
    st.markdown(
        f"""
        <div style="
            background-color: #DFF2BF;
            border-radius: 15px;
            padding: 10px;
            margin-bottom: 10px;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
        ">
            <strong>{cliente['Nombre']}</strong><br>
            Probabilidad de Deterioro: {prob}<br>
            Nivel Atraso: {cliente.get("Nivel Atraso", "N/A")}<br>
            Edad Cliente: {cliente.get("Edad Cliente", "N/A")}<br>
            Entidad Federativa: {cliente.get("Entidad Federativa", "N/A")}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(f"Ver {cliente['Nombre']}", key=f"ver_cliente_{cliente['Solicitud Id']}"):
        st.session_state["cliente_seleccionado"] = cliente
        st.session_state["pantalla_actual"] = "informacion_cliente"
        st.experimental_rerun()

# Pantalla de lista completa de clientes
def pantallaListaClientes(sheet):
    st.title("Lista de Clientes")
    if "clientes" not in st.session_state or not st.session_state["clientes"]:
        st.error("No hay clientes asignados.")
        return

    filtro = st.selectbox("Filtrar por", ["Sin Filtro", "Entidad Federativa", "Edad Cliente"])
    clientes = st.session_state["clientes"]

    if filtro == "Edad Cliente":
        # Corrección para ordenar y mostrar clientes
        clientes = sorted(clientes, key=lambda x: x.get("Edad Cliente", 0), reverse=True)
        for cliente in clientes:
            mostrarCliente(cliente)
    elif filtro == "Entidad Federativa":
        entidades = sorted(set(fila["Entidad Federativa"] for fila in clientes))
        for entidad in entidades:
            with st.expander(f"Clientes en {entidad}"):
                clientes_entidad = [fila for fila in clientes if fila["Entidad Federativa"] == entidad]
                for cliente in clientes_entidad:
                    mostrarCliente(cliente)
    else:
        for cliente in clientes:
            mostrarCliente(cliente)

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "inicio"
        st.experimental_rerun()

# Pantalla de información del cliente
def pantallaInformacionCliente(sheet):
    cliente = st.session_state.get("cliente_seleccionado", None)
    if not cliente:
        st.error("No se encontró el cliente seleccionado.")
        return

    tipo_gestor = st.session_state.get("role", "").lower()
    gestionado = "Sí" if cliente.get("Gestionado", 0) == 1 else "No"

    st.title(f"Información de {cliente['Nombre']}")
    st.write("Gestionado:", gestionado)
    st.write("Offer Recommendation:", cliente["Offer Recommendation"])

    if tipo_gestor == "puerta":
        st.image("DimiFoto.jpeg", width=200)
        st.write("Deuda:", cliente.get("Deuda", "N/A"))
        st.write("Nivel Atraso:", cliente.get("Nivel Atraso", "N/A"))
    elif tipo_gestor == "llamada":
        st.write("Solicitud Id:", cliente.get("Solicitud Id", "N/A"))  # Corrección del nombre
        st.write("Deuda:", cliente.get("Deuda", "N/A"))
        st.write("Pago:", cliente.get("Pago", "N/A"))

    if st.button("Registrar Interacción"):
        st.session_state["pantalla_actual"] = "formulario_interaccion"
        st.experimental_rerun()

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "lista_clientes"
        st.experimental_rerun()

# Pantalla de formulario para registrar interacción
def pantallaFormularioInteraccion(sheet):
    cliente = st.session_state.get("cliente_seleccionado", None)
    if not cliente:
        st.error("No se encontró el cliente seleccionado.")
        return

    st.title(f"Registrar Interacción - {cliente['Nombre']}")

    tipo_gestion = st.selectbox("Tipo de Gestión", ["Call Center", "Gestion Puerta a Puerta"])
    resultado = st.selectbox("Resultado", ["Atendio un tercero", "No localizado", "Atendio cliente"])
    promesa = st.selectbox("Promesa", ["Si", "No"])
    oferta = st.selectbox(
        "Oferta de Cobranza",
        ["Reestructura del Credito", "Tus Pesos Valen Mas", "Pago sin Beneficio", "Quita / Castigo", "No acordo"]
    )
    fecha_acordada = st.date_input("Fecha Acordada", min_value=date.today())

    if st.button("Guardar"):
        interaccion = {
            "Tipo_Gestion": tipo_gestion,
            "Resultado": resultado,
            "Promesa_Pago": promesa,
            "Oferta_Cobranza": oferta,
            "Fecha_Acordada": fecha_acordada.strftime("%d/%m/%Y"),
            "Fecha_Interaccion": date.today().strftime("%d/%m/%Y")
        }

        interacciones_actuales = json.loads(cliente.get("Interacciones", "[]")) if cliente.get("Interacciones") else []
        interacciones_actuales.append(interaccion)

        fila = next(
            (i + 2 for i, fila in enumerate(leerDatos(sheet)) if fila["Solicitud Id"] == cliente["Solicitud Id"]),
            None
        )

        if fila:
            actualizarGoogleSheets(sheet, fila, obtenerIndiceColumna(sheet, "Interacciones"), json.dumps(interacciones_actuales))
            actualizarGoogleSheets(sheet, fila, obtenerIndiceColumna(sheet, "Gestionado"), 1)
            st.success("Interacción registrada correctamente.")
            st.session_state["pantalla_actual"] = "informacion_cliente"
            st.experimental_rerun()
        else:
            st.error("Error al actualizar la interacción.")

# Flujo principal de la aplicación
def flujoPantallas(sheet):
    if "pantalla_actual" not in st.session_state:
        st.session_state["pantalla_actual"] = "inicio"

    if st.session_state["pantalla_actual"] == "inicio":
        pantallaInicioSesion(sheet)
    elif st.session_state["pantalla_actual"] == "resumen_admin":
        pantallaResumenAdministrador(sheet)
    elif st.session_state["pantalla_actual"] == "lista_clientes":
        pantallaListaClientes(sheet)
    elif st.session_state["pantalla_actual"] == "informacion_cliente":
        pantallaInformacionCliente(sheet)
    elif st.session_state["pantalla_actual"] == "formulario_interaccion":
        pantallaFormularioInteraccion(sheet)

# Conectar con Google Sheets y ejecutar el flujo
sheet = conectarGoogleSheets()
flujoPantallas(sheet)