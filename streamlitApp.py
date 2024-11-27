import streamlit as st

def verificarCredenciales(usuario, contrasena):
    # Función simulada para verificar credenciales (prototipo)
    return usuario == "usuarioDemo" and contrasena == "contrasenaDemo"

def mostrarPantallaInicioSesion():
    st.title("Inicio de Sesión")
    st.write("Por favor, ingresa tus credenciales para acceder a la aplicación.")

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")
    inicioSesion = st.button("Iniciar Sesión")

    if inicioSesion:
        if verificarCredenciales(usuario, contrasena):
            st.session_state['authenticated'] = True
            st.session_state['pagina'] = 'dashboard'
            st.experimental_rerun()
        else:
            st.error("Credenciales inválidas. Por favor, intenta de nuevo.")

    if st.checkbox("¿Olvidaste tu contraseña?"):
        st.info("Contacta al administrador para recuperar tu contraseña.")

    st.write("🔒 Esta es una conexión segura. Protege tus credenciales.")

def mostrarDashboardGestor():
    st.header("Dashboard del Gestor")
    st.subheader("Resumen del Gestor")
    st.write("Nombre del gestor: Juan Pérez")
    st.write("Rol: Gestor de Cobranza")

    # Organización de métricas en columnas para mejor visualización en móviles
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Clientes Asignados", 50)
    with col2:
        st.metric("Metas de Cobranza", "75% completado")

    st.subheader("Clientes Pendientes")
    st.write("Lista de clientes con pagos atrasados")
    st.dataframe({
        "Cliente": ["Cliente A", "Cliente B", "Cliente C"],
        "Días de Atraso": [15, 30, 45],
        "Última Interacción": ["Llamada", "Correo", "Visita"],
        "Status": ["En proceso", "Pendiente", "Crítico"]
    })

    st.subheader("Notificaciones y Alertas")
    st.warning("Cliente B tiene un pago próximo a vencer.")
    st.error("Cliente C requiere atención urgente.")

    # Botón para acceder a la lista de clientes dentro de un contenedor
    with st.container():
        if st.button("Ver Lista de Clientes"):
            st.session_state['pagina'] = 'lista_clientes'
            st.experimental_rerun()

    # Botón para cerrar sesión
    if st.button("Cerrar Sesión"):
        st.session_state['pagina'] = 'inicio_sesion'
        st.session_state['authenticated'] = False
        st.experimental_rerun()

def mostrarListaClientes():
    st.title("Lista de Clientes")
    st.write("Aquí puedes ver y gestionar la lista completa de clientes.")
    clientes = ["Cliente A", "Cliente B", "Cliente C", "Cliente D"]
    diasAtraso = [15, 30, 45, 60]
    ultimaInteraccion = ["Llamada", "Correo", "Visita", "Llamada"]
    status = ["En proceso", "Pendiente", "Crítico", "En proceso"]
    data = {
        "Cliente": clientes,
        "Días de Atraso": diasAtraso,
        "Última Interacción": ultimaInteraccion,
        "Status": status
    }
    st.dataframe(data)

    # Botón para seleccionar un cliente y ver detalles
    seleccionCliente = st.selectbox("Selecciona un cliente para ver sus interacciones:", clientes)

    if st.button("Ver Interacciones del Cliente") and seleccionCliente:
        st.session_state['cliente_seleccionado'] = seleccionCliente
        st.session_state['pagina'] = 'interacciones'
        st.experimental_rerun()

    # Botón para volver al dashboard
    if st.button("Volver al Dashboard"):
        st.session_state['pagina'] = 'dashboard'
        st.experimental_rerun()

def mostrarInteraccionesCliente():
    st.title(f"Interacciones con {st.session_state['cliente_seleccionado']}")
    st.write("Registra una nueva interacción con el cliente.")

    with st.form("form_interaccion"):
        # Pregunta 1
        tipoGestion = st.selectbox("Tipo de gestion", ["Agencias Especializadas", "Call Center", "Gestion Puerta a Puerta"])
        
        # Pregunta 2
        resultadoGestion = st.selectbox("Resultado", ["No atendio", "Atendio cliente", "Atendio un tercero"])
        
        # Pregunta 3
        promesaPago = st.selectbox("Promesa pago", ["Si", "No"])

        enviar = st.form_submit_button("Registrar Interacción")

        if enviar:
            # Crear el diccionario para almacenar las respuestas
            interaccion = {
                "Tipo de gestion": tipoGestion,
                "Resultado": resultadoGestion,
                "Promesa pago": promesaPago
            }

            st.success("Interacción registrada exitosamente.")
            st.session_state['pagina'] = 'lista_clientes'
            st.experimental_rerun()

    # Botón para volver a la lista de clientes
    if st.button("Volver a la Lista de Clientes"):
        st.session_state['pagina'] = 'lista_clientes'
        st.experimental_rerun()

# Configuración inicial de session_state para controlar la navegación
if 'pagina' not in st.session_state:
    st.session_state['pagina'] = 'inicio_sesion'

# Navegación entre pantallas
if st.session_state['pagina'] == 'inicio_sesion':
    mostrarPantallaInicioSesion()
elif st.session_state['pagina'] == 'dashboard':
    mostrarDashboardGestor()
elif st.session_state['pagina'] == 'lista_clientes':
    mostrarListaClientes()
elif st.session_state['pagina'] == 'interacciones':
    mostrarInteraccionesCliente()
