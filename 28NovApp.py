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
        elif username in gestores['Gestor'].values and password == "gestor":
            st.session_state["role"] = username
            st.session_state["clientes"] = df[df['Gestor'] == username]
            st.session_state["pantalla_actual"] = "lista_clientes"
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

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "inicio"

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

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "inicio"

# Pantalla de lista completa de clientes
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
            # Guardar el cliente seleccionado en el estado
            st.session_state["cliente_seleccionado"] = cliente
            st.session_state["pantalla_actual"] = "informacion_cliente"
            st.experimental_rerun()

    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "inicio"
        st.experimental_rerun()

# Pantalla de información específica del cliente diferenciada por tipo de gestor
# Pantalla de información específica del cliente diferenciada por tipo de gestor
# Pantalla de información específica del cliente diferenciada por tipo de gestor
def pantallaInformacionCliente(df):
    cliente = st.session_state.get("cliente_seleccionado", None)

    # Validar cliente seleccionado
    if cliente is None or not isinstance(cliente, pd.Series):
        st.error("No se encontró el cliente seleccionado.")
        st.session_state["pantalla_actual"] = "lista_clientes"
        st.experimental_rerun()
        return

    st.title(f"Información de {cliente['Nombre']}")
    gestionado = "Sí" if cliente["Gestionado"] == 1 else "No"
    st.write("Gestionado:", gestionado)
    st.write("Offer Recommendation:", cliente.get("Offer Recommendation", "N/A"))

    # Mostrar información específica del gestor
    tipo_gestor = st.session_state.get("role", "").lower()
    if tipo_gestor == "puerta":
        st.subheader("Información para Gestor Puerta a Puerta")
        st.write("Nivel Atraso:", cliente.get("Nivel Atraso", "N/A"))
        st.write("Ultima Gestion:", cliente.get("Ultima Gestion", "N/A"))
    elif tipo_gestor == "llamada":
        st.subheader("Información para Gestor Call Center")
        st.write("Estado de Cuenta:", cliente.get("Estado Cuenta", "N/A"))
        st.write("Probabilidad de Contención:", cliente.get("Probabilidad Contención", "N/A"))
        st.write("Nivel Atraso:", cliente.get("Nivel Atraso", "N/A"))
        st.write("Ultima Gestion:", cliente.get("Ultima Gestion", "N/A"))
        st.write("Promesas de Pago (Sí):", cliente.get("Promesa Pago Si", "N/A"))
        st.write("Número de Interacciones:", cliente.get("Num Interacciones", "N/A"))

    # Botón para registrar interacción
    if st.button("Registrar Interacción"):
        st.session_state["pantalla_actual"] = "formulario_interaccion"
        st.experimental_rerun()

    # Botón de regresar
    if st.button("Regresar"):
        st.session_state["pantalla_actual"] = "lista_clientes"
        st.experimental_rerun()

# Pantalla de formulario para registrar interacción
# Pantalla de formulario para registrar interacción
# Pantalla de formulario para registrar interacción
def pantallaFormularioInteraccion(df):
    cliente = st.session_state.get("cliente_seleccionado", None)

    # Validar el cliente seleccionado
    if cliente is None or not isinstance(cliente, pd.Series):
        st.error("No se encontró el cliente seleccionado.")
        st.session_state["pantalla_actual"] = "lista_clientes"
        st.experimental_rerun()
        return

    st.title(f"Registrar Interacción - {cliente['Nombre']}")

    # Formulario para registrar la interacción
    with st.form(key="form_interaccion"):
        tipo_gestion = st.selectbox("Tipo de Gestión", ["Call Center", "Gestion Puerta a Puerta"])
        resultado = st.selectbox("Resultado", ["Atendio un tercero", "No localizado", "Atendio cliente"])
        promesa = st.selectbox("Promesa", ["Si", "No"])
        oferta = st.selectbox("Oferta de Cobranza", ["Reestructura del Credito", "Tus Pesos Valen Mas", "Quita / Castigo", "Pago sin Beneficio"])
        fecha_acordada = st.date_input("Fecha Acordada")
        fecha_interaccion = st.date_input("Fecha de la Interacción")

        if st.form_submit_button("Guardar"):
            # Añadir la interacción al cliente
            nueva_interaccion = {
                "Tipo_Gestion": tipo_gestion,
                "Resultado": resultado,
                "Promesa_Pago": promesa,
                "Oferta_Cobranza": oferta,
                "Fecha_Acordada": fecha_acordada.strftime('%Y-%m-%d'),
                "Fecha_Interaccion": fecha_interaccion.strftime('%Y-%m-%d'),
            }

            interacciones = json.loads(cliente["Interacciones"]) if cliente["Interacciones"] else []
            interacciones.append(nueva_interaccion)

            # Actualizar el DataFrame
            df.loc[df["Solicitud Id"] == cliente["Solicitud Id"], "Interacciones"] = json.dumps(interacciones)
            st.success("Interacción registrada correctamente.")

    # Botón de regresar
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
