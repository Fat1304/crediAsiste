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
    sheet = client.open("DemoDimi").sheet1  # Cambia al nombre de tu Google Sheets
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
    cabeceras = sheet.row_values(1)  # Suponiendo que la primera fila tiene los nombres de las columnas
    if nombre_columna in cabeceras:
        return cabeceras.index(nombre_columna) + 1  # Las columnas comienzan en 1
    else:
        raise ValueError(f"La columna '{nombre_columna}' no existe en la hoja.")

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

# Pantalla inicial del gestor
def pantallaInicialGestor(sheet):
    st.title(f"Gestor: {st.session_state['role']}")
    if "clientes" not in st.session_state or not st.session_state["clientes"]:
        st.error("No hay clientes asignados para este gestor.")
        return
    
    clientes = st.session_state["clientes"]
    gestionados = sum(1 for fila in clientes if fila["Gestionado"] == 1)
    progreso = (gestionados / len(clientes)) * 100
    st.metric("Progreso de Gestión", f"{gestionados} de {len(clientes)}", f"{progreso:.2f}%")

    st.subheader("Clientes Asignados")
    st.table([{"Nombre": fila["Nombre"], "Probabilidad": fila["Probabilidad Cuenta Deteriorada"]} for fila in clientes[:5]])

    if st.button("Ver Lista Completa"):
        st.session_state["pantalla_actual"] = "lista_clientes"
        st.experimental_rerun()

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "inicio"
        st.experimental_rerun()

# Pantalla de lista completa de clientes
def pantallaListaClientes(sheet):
    st.title("Lista de Clientes")
    if "clientes" not in st.session_state or not st.session_state["clientes"]:
        st.error("No hay clientes asignados.")
        return

    clientes = st.session_state["clientes"]
    for cliente in clientes:
        prob = cliente.get("Probabilidad Cuenta Deteriorada", 0)
        interacciones = cliente.get("Num Interacciones", 0)
        promesa_pago_si = cliente.get("Promesa Pago Si", 0)
        gestionado = "Sí" if cliente.get("Gestionado", 0) == 1 else "No"

        if prob <= 0.30:
            color = "#DFF2BF"  # Verde clarito
        elif prob <= 0.70:
            color = "#FFFFCC"  # Amarillo clarito
        else:
            color = "#FFBABA"  # Rojo clarito

        st.markdown(
            f"""
            <div style="
                background-color: {color};
                border-radius: 15px;
                padding: 10px;
                margin-bottom: 10px;
                box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
            ">
                <strong>{cliente['Nombre']}</strong><br>
                Probabilidad de Deterioro: {prob:.2f}<br>
                Número de Interacciones: {interacciones}<br>
                Promesas de Pago (Sí): {promesa_pago_si}<br>
                Gestionado: {gestionado}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(f"Ver {cliente['Nombre']}", key=f"ver_cliente_{cliente['Solicitud Id']}"):
            st.session_state["cliente_seleccionado"] = cliente
            st.session_state["pantalla_actual"] = "informacion_cliente"
            st.experimental_rerun()

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "inicio"
        st.experimental_rerun()

# Pantalla de información específica del cliente diferenciada por tipo de gestor
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
        st.subheader("Editar Información del Cliente")
        nuevo_nombre = st.text_input("Nombre", cliente.get("Nombre", ""))
        nueva_direccion = st.text_input("Direccion", cliente.get("Direccion", ""))
        nuevo_telefono = st.text_input("Telefono", cliente.get("Telefono", ""))

        if st.button("Guardar Cambios"):
            try:
                fila = next(
                    (i + 2 for i, fila in enumerate(leerDatos(sheet)) if fila["Solicitud Id"] == cliente["Solicitud Id"]),
                    None
                )
                if not fila:
                    st.error("No se encontró la fila del cliente en Google Sheets.")
                    return

                actualizarGoogleSheets(sheet, fila, obtenerIndiceColumna(sheet, "Nombre"), nuevo_nombre)
                actualizarGoogleSheets(sheet, fila, obtenerIndiceColumna(sheet, "Direccion"), nueva_direccion)
                actualizarGoogleSheets(sheet, fila, obtenerIndiceColumna(sheet, "Telefono"), nuevo_telefono)

                st.success("Información del cliente actualizada correctamente.")
                
                data = leerDatos(sheet)
                st.session_state["clientes"] = [
                    fila for fila in data if fila.get("Gestor", "").strip().lower() == st.session_state["role"].lower()
                ]
                cliente_actualizado = next(
                    (fila for fila in st.session_state["clientes"] if fila["Solicitud Id"] == cliente["Solicitud Id"]), None
                )
                if cliente_actualizado:
                    st.session_state["cliente_seleccionado"] = cliente_actualizado
                    st.experimental_rerun()

            except Exception as e:
                st.error(f"Error al actualizar la información del cliente: {e}")

    elif tipo_gestor == "llamada":
        st.subheader("Información para Gestor Call Center")
        st.write("Estado de Cuenta:", cliente.get("Estado Cuenta", "N/A"))
        st.write("Probabilidad de Contención:", cliente.get("Probabilidad Contención", "N/A"))
        st.write("Nivel Atraso:", cliente.get("Nivel Atraso", "N/A"))
        st.write("Ultima Gestion:", cliente.get("Ultima Gestion", "N/A"))
        st.write("Promesas de Pago (Sí):", cliente.get("Promesa Pago Si", "N/A"))
        st.write("Número de Interacciones:", cliente.get("Num Interacciones", "N/A"))

    interacciones = json.loads(cliente.get("Interacciones", "[]"))
    interacciones_filtradas = [i for i in interacciones if len(i.keys()) <= 3]

    if interacciones_filtradas:
        st.subheader("Historial de Interacciones")
        st.table(interacciones_filtradas)
    else:
        st.info("No hay interacciones disponibles para mostrar.")

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

        try:
            interacciones_actuales = json.loads(cliente["Interacciones"]) if cliente["Interacciones"] else []
            if not isinstance(interacciones_actuales, list):
                raise ValueError("El campo 'Interacciones' no es una lista válida.")
            interacciones_actuales.append(interaccion)
        except Exception as e:
            st.warning(f"Formato inválido en 'Interacciones'. Inicializando como lista vacía. Error: {e}")
            interacciones_actuales = [interaccion]

        fila = next(
            (i + 2 for i, fila in enumerate(leerDatos(sheet)) if fila["Solicitud Id"] == cliente["Solicitud Id"]),
            None
        )
        if not fila:
            st.error("No se encontró la fila del cliente en Google Sheets.")
            return

        try:
            actualizarGoogleSheets(sheet, fila, obtenerIndiceColumna(sheet, "Interacciones"), json.dumps(interacciones_actuales))
            actualizarGoogleSheets(sheet, fila, obtenerIndiceColumna(sheet, "Gestionado"), 1)
            st.success("Datos actualizados correctamente en Google Sheets.")
        except Exception as e:
            st.error(f"Error al actualizar Google Sheets: {e}")
            return

        data = leerDatos(sheet)
        st.session_state["clientes"] = [
            fila for fila in data if fila.get("Gestor", "").strip().lower() == st.session_state["role"].lower()
        ]
        cliente_actualizado = next(
            (fila for fila in st.session_state["clientes"] if fila["Solicitud Id"] == cliente["Solicitud Id"]), None
        )
        if cliente_actualizado:
            st.session_state["cliente_seleccionado"] = cliente_actualizado

        st.session_state["pantalla_actual"] = "informacion_cliente"
        st.experimental_rerun()

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "informacion_cliente"
        st.experimental_rerun()

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
