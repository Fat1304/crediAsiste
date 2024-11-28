import streamlit as st
import pandas as pd
import json

# URL del archivo CSV en GitHub
URL_CSV = "https://raw.githubusercontent.com/Fat1304/crediAsiste/master/dimiDatos.csv"

# Leer datos del CSV en GitHub
def leerDatos():
    try:
        df = pd.read_csv(URL_CSV)
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo CSV: {e}")
        return None

# Pantalla de inicio de sesión
def pantallaInicioSesion(df):
    st.title("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        gestores = df[df['Gestor'].notna()]

        if username == "admin" and password == "admin":
            st.session_state["role"] = "admin"
            st.session_state["pantalla_actual"] = "resumen_admin"
            st.experimental_rerun()
        elif username in gestores['Gestor'].values and password == "gestor":
            st.session_state["role"] = username
            st.session_state["clientes"] = df[df['Gestor'] == username]
            st.session_state["pantalla_actual"] = "lista_clientes"
            st.experimental_rerun()
        else:
            st.error("Credenciales incorrectas")

# Pantalla de resumen del administrador
def pantallaResumenAdministrador(df):
    st.title("Resumen General - Administrador")

    total_clientes = len(df)
    gestionados = df[df["Gestionado"] == 1]
    porcentaje = (len(gestionados) / total_clientes) * 100
    monto_total_deuda = df["Deuda"].sum()

    st.metric("Clientes Gestionados", f"{len(gestionados)} de {total_clientes}", f"{porcentaje:.2f}%")
    st.metric("Monto Total de la Deuda", f"${monto_total_deuda:,.2f}")

    st.header("Lista de Gestores")
    gestores = df["Gestor"].unique()
    for gestor in gestores:
        if st.button(f"Ver {gestor}"):
            st.session_state["clientes"] = df[df["Gestor"] == gestor]
            st.session_state["pantalla_actual"] = "lista_clientes"
            st.experimental_rerun()

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "inicio"
        st.experimental_rerun()

# Pantalla inicial del gestor
def pantallaInicialGestor(df):
    st.title(f"Gestor: {st.session_state['role']}")
    if "clientes" not in st.session_state or st.session_state["clientes"].empty:
        st.error("No hay clientes asignados para este gestor.")
        return
    
    clientes = st.session_state["clientes"]
    gestionados = clientes[clientes["Gestionado"] == 1]
    progreso = (len(gestionados) / len(clientes)) * 100
    st.metric("Progreso de Gestión", f"{len(gestionados)} de {len(clientes)}", f"{progreso:.2f}%")

    st.subheader("Clientes Asignados")
    st.table(clientes[["Nombre", "Probabilidad Cuenta Deteriorada"]].head(5))

    if st.button("Ver Lista Completa"):
        st.session_state["pantalla_actual"] = "lista_clientes"
        st.experimental_rerun()

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "inicio"
        st.experimental_rerun()

# Pantalla de lista completa de clientes
def pantallaListaClientes(df):
    st.title("Lista de Clientes")
    if "clientes" not in st.session_state or st.session_state["clientes"].empty:
        st.error("No hay clientes asignados.")
        return

    clientes = st.session_state["clientes"]
    for _, cliente in clientes.iterrows():
        prob = cliente["Probabilidad Cuenta Deteriorada"]
        interacciones = cliente["Num Interacciones"]
        promesa_pago_si = cliente["Promesa Pago Si"]
        gestionado = "Sí" if cliente["Gestionado"] == 1 else "No"

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
def pantallaInformacionCliente(df):
    cliente = st.session_state.get("cliente_seleccionado", None)
    if cliente is None or cliente.empty:
        st.error("No se encontró el cliente seleccionado.")
        return

    tipo_gestor = st.session_state.get("role", "")
    gestionado = "Sí" if cliente.get("Gestionado", 0) == 1 else "No"
    st.title(f"Información de {cliente['Nombre']}")
    st.write("Gestionado:", gestionado)
    st.write("Offer Recommendation:", cliente["Offer Recommendation"])

    # Botón de "Regresar"
    if st.button("Regresar"):
        # Aquí puedes redirigir a una página de clientes o al dashboard, dependiendo de la estructura de tu aplicación
        st.session_state.cliente_seleccionado = None  # Limpia la selección actual del cliente
        st.experimental_rerun()  # Vuelve a cargar la página anterior

    # Mostrar los datos según el tipo de gestor
    if tipo_gestor.lower() == "puerta":
        st.subheader("Información para Gestor Puerta a Puerta")
        st.write("Nivel Atraso:", cliente.get("Nivel Atraso", "N/A"))
        st.write("Ultima Gestion:", cliente.get("Ultima Gestion", "N/A"))
    elif tipo_gestor.lower() == "llamada":
        st.subheader("Información para Gestor Call Center")
        st.write("Estado de Cuenta:", cliente.get("Estado Cuenta", "N/A"))
        st.write("Probabilidad de Contención:", cliente.get("Probabilidad Contención", "N/A"))
        st.write("Nivel Atraso:", cliente.get("Nivel Atraso", "N/A"))
        st.write("Ultima Gestion:", cliente.get("Ultima Gestion", "N/A"))
        st.write("Promesas de Pago (Sí):", cliente.get("Promesa Pago Si", "N/A"))
        st.write("Número de Interacciones:", cliente.get("Num Interacciones", "N/A"))

    # Mostrar el historial de interacciones
    interacciones = json.loads(cliente.get("Interacciones", "[]"))
    interacciones_filtradas = [i for i in interacciones if len(i.keys()) <= 3]

    if interacciones_filtradas:
        st.subheader("Historial de Interacciones")
        st.table(interacciones_filtradas)
    else:
        st.info("No hay interacciones disponibles para mostrar.")
    
    # Formulario para ingresar una nueva interacción
    with st.form(key='form_interaccion'):
        st.subheader("Registrar nueva interacción")

        # Campos del formulario
        tipo_gestion = st.selectbox("Tipo de Gestión", ["Call Center", "Gestion Puerta a Puerta"])
        resultado = st.selectbox("Resultado de la Interacción", ["Atendio un tercero", "No localizado", "Atendio cliente"])
        promesa = st.selectbox("Promesa de Pago", ["Sí", "No"])

        # Campos adicionales
        oferta_cobranza = st.text_input("Oferta de Cobranza")
        fecha_acordada = st.date_input("Fecha Acordada")
        fecha_interaccion = st.date_input("Fecha de la Interacción")

        # Botón de envío del formulario
        submit_button = st.form_submit_button("Registrar Interacción")

        if submit_button:
            # Registrar la interacción en el cliente
            nueva_interaccion = {
                "Tipo_Gestion": tipo_gestion,
                "Resultado": resultado,
                "Promesa": promesa,
                "Oferta_Cobranza": oferta_cobranza,
                "Fecha_Acordada": fecha_acordada.strftime('%Y-%m-%d'),
                "Fecha_Interaccion": fecha_interaccion.strftime('%Y-%m-%d')
            }

            # Actualizar la lista de interacciones
            interacciones.append(nueva_interaccion)
            cliente["Interacciones"] = json.dumps(interacciones)  # Convertir a JSON

            # Guardar el cliente con la nueva interacción
            df.loc[df["Nombre"] == cliente["Nombre"], "Interacciones"] = json.dumps(interacciones)
            st.success("Interacción registrada exitosamente.")
            st.experimental_rerun()  # Recargar la página después de registrar la interacción

# Pantalla de formulario para registrar interacción
def pantallaFormularioInteraccion(df):
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
            "Fecha_Acordada": fecha_acordada,
            "Fecha_Interaccion": str(date.today())
        }
        interacciones = json.loads(cliente["Interacciones"]) if cliente["Interacciones"] else []
        interacciones.append(interaccion)

        df.loc[df["Solicitud Id"] == cliente["Solicitud Id"], "Interacciones"] = json.dumps(interacciones)
        st.success("Interacción registrada correctamente.")

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "informacion_cliente"
        st.experimental_rerun()

# Main
def main():
    if "pantalla_actual" not in st.session_state:
        st.session_state["pantalla_actual"] = "inicio"

    df = leerDatos()

    if df is not None:
        if st.session_state["pantalla_actual"] == "inicio":
            pantallaInicioSesion(df)
        elif st.session_state["pantalla_actual"] == "resumen_admin":
            pantallaResumenAdministrador(df)
        elif st.session_state["pantalla_actual"] == "lista_clientes":
            pantallaListaClientes(df)
        elif st.session_state["pantalla_actual"] == "informacion_cliente":
            pantallaInformacionCliente(df)
        elif st.session_state["pantalla_actual"] == "formulario_interaccion":
            pantallaFormularioInteraccion(df)

if __name__ == "__main__":
    main()