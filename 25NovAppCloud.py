import streamlit as st
from datetime import date
import json

# Integración con Google Sheets
from streamlit.connections.experimental import GSheetsConnection

# Crear la conexión con Google Sheets
def conectarGoogleSheets():
    conn = st.connection("gsheets", type=GSheetsConnection)
    sheet = conn.read()
    return sheet

# Leer datos del Google Sheets
def leerDatos(sheet):
    return sheet.to_dict(orient="records")

# Actualizar una celda específica en Google Sheets
def actualizarGoogleSheets(sheet, fila, columna, valor):
    try:
        sheet.loc[fila, columna] = valor  # Actualiza directamente en el dataframe local
        st.success(f"Celda actualizada: fila {fila}, columna {columna}")
    except Exception as e:
        st.error(f"Error al actualizar Google Sheets: {e}")

# Obtener índice de una columna basada en su nombre
def obtenerIndiceColumna(sheet, nombre_columna):
    if nombre_columna in sheet.columns:
        return sheet.columns.get_loc(nombre_columna)
    else:
        raise ValueError(f"La columna '{nombre_columna}' no existe en la hoja.")

# Pantalla de inicio de sesión
def pantallaInicioSesion(sheet):
    st.title("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        data = leerDatos(sheet)
        gestores = {fila["Gestor"]: fila for fila in data if fila.get("Gestor")}

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
    gestionados = sum(1 for fila in data if fila.get("Gestionado") == 1)
    porcentaje = (gestionados / total_clientes) * 100 if total_clientes > 0 else 0
    monto_total_deuda = sum(float(fila.get("Deuda", 0)) for fila in data)

    st.metric("Clientes Gestionados", f"{gestionados} de {total_clientes}", f"{porcentaje:.2f}%")
    st.metric("Monto Total de la Deuda", f"${monto_total_deuda:,.2f}")

    st.header("Lista de Gestores")
    gestores = set(fila["Gestor"] for fila in data if fila.get("Gestor"))
    for gestor in gestores:
        if st.button(f"Ver {gestor}"):
            st.session_state["clientes"] = [fila for fila in data if fila["Gestor"] == gestor]
            st.session_state["pantalla_actual"] = "lista_clientes"
            st.experimental_rerun()

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "inicio"
        st.experimental_rerun()

# Pantalla inicial del gestor
def pantallaInicialGestor(sheet):
    st.title(f"Gestor: {st.session_state['role']}")
    if "clientes" not in st.session_state or not st.session_state["clientes"]:
        st.error("No hay clientes asignados para este gestor.")
        return
    
    clientes = st.session_state["clientes"]
    gestionados = sum(1 for fila in clientes if fila.get("Gestionado") == 1)
    progreso = (gestionados / len(clientes)) * 100 if clientes else 0
    st.metric("Progreso de Gestión", f"{gestionados} de {len(clientes)}", f"{progreso:.2f}%")

    st.subheader("Clientes Asignados")
    st.table([{"Nombre": fila["Nombre"], "Probabilidad": fila.get("Probabilidad Cuenta Deteriorada", 0)} for fila in clientes[:5]])

    if st.button("Ver Lista Completa"):
        st.session_state["pantalla_actual"] = "lista_clientes"
        st.experimental_rerun()

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "inicio"
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

        try:
            interacciones_actuales = json.loads(cliente["Interacciones"]) if cliente["Interacciones"] else []
            if not isinstance(interacciones_actuales, list):
                raise ValueError("El campo 'Interacciones' no es una lista válida.")
            interacciones_actuales.append(interaccion)
        except Exception as e:
            st.warning(f"Formato inválido en 'Interacciones'. Inicializando como lista vacía. Error: {e}")
            interacciones_actuales = [interaccion]

        fila = next(
            (i for i, fila in enumerate(leerDatos(sheet)) if fila["Solicitud Id"] == cliente["Solicitud Id"]),
            None
        )
        if fila is None:
            st.error("No se encontró la fila del cliente en Google Sheets.")
            return

        try:
            actualizarGoogleSheets(sheet, fila, "Interacciones", json.dumps(interacciones_actuales))
            actualizarGoogleSheets(sheet, fila, "Gestionado", 1)
            st.success("Datos actualizados correctamente en Google Sheets.")
        except Exception as e:
            st.error(f"Error al actualizar Google Sheets: {e}")
            return

        st.session_state["pantalla_actual"] = "informacion_cliente"
        st.experimental_rerun()

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "informacion_cliente"
        st.experimental_rerun()

# Flujo principal de la aplicación
def flujoPantallas():
    if "pantalla_actual" not in st.session_state:
        st.session_state["pantalla_actual"] = "inicio"

    sheet = conectarGoogleSheets()
    if st.session_state["pantalla_actual"] == "inicio":
        pantallaInicioSesion(sheet)
    elif st.session_state["pantalla_actual"] == "resumen_admin":
        pantallaResumenAdministrador(sheet)
    elif st.session_state["pantalla_actual"] == "lista_clientes":
        pantallaListaClientes(sheet)
    elif st.session_state["pantalla_actual"] == "formulario_interaccion":
        pantallaFormularioInteraccion(sheet)

# Ejecutar el flujo
flujoPantallas()
