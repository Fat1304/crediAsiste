import streamlit as st

# Diccionario de usuarios y contraseñas con roles
usuariosValidos = {
    "admin": {"password": "admin123", "rol": "Administrador"},
    "gestor1": {"password": "puerta123", "rol": "Gestor Puerta por Puerta"},
    "gestor2": {"password": "call123", "rol": "Gestor Call Center"}
}

def verificarCredenciales(usuario, contrasena):
    if usuario in usuariosValidos and usuariosValidos[usuario]["password"] == contrasena:
        return usuariosValidos[usuario]["rol"]
    return None

def mostrarInicioSesion():
    st.title("Inicio de Sesión")
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")
    iniciarSesion = st.button("Iniciar Sesión")

    if iniciarSesion:
        rol = verificarCredenciales(usuario, contrasena)
        if rol:
            st.session_state['rol'] = rol
            st.session_state['pagina'] = 'dashboard'
            st.experimental_rerun()
        else:
            st.error("Credenciales inválidas. Por favor, intenta de nuevo.")

class Administrador:
    def mostrarDashboard(self):
        st.title("Panel de Administrador")
        st.write("Bienvenido, administrador.")
        if st.button("Ver asignaciones de clientes"):
            st.write("Lista de clientes asignados a cada gestor.")
        if st.button("Modificar asignaciones de clientes"):
            st.write("Herramienta para modificar asignaciones.")
        if st.button("Cerrar sesión"):
            st.session_state['pagina'] = 'inicioSesion'
            st.experimental_rerun()

class GestorPuertaPuerta:
    def mostrarDashboard(self):
        st.title("Gestor Puerta por Puerta")
        st.write("Bienvenido, gestor de campo.")
        if st.button("Ver lista de clientes"):
            st.write("Lista de clientes asignados para visitas.")
        if st.button("Registrar nueva interacción"):
            st.write("Formulario para registrar una interacción.")
        if st.button("Cerrar sesión"):
            st.session_state['pagina'] = 'inicioSesion'
            st.experimental_rerun()

class GestorCallCenter:
    def mostrarDashboard(self):
        st.title("Gestor Call Center")
        st.write("Bienvenido, gestor de llamadas.")
        if st.button("Recibir llamada"):
            st.write("Formulario para registrar datos de la llamada.")
        if st.button("Ver lista de clientes"):
            st.write("Lista de clientes asignados para gestión telefónica.")
        if st.button("Cerrar sesión"):
            st.session_state['pagina'] = 'inicioSesion'
            st.experimental_rerun()

def ejecutarAplicacion():
    if 'pagina' not in st.session_state:
        st.session_state['pagina'] = 'inicioSesion'

    if st.session_state['pagina'] == 'inicioSesion':
        mostrarInicioSesion()
    elif st.session_state['pagina'] == 'dashboard':
        if 'rol' in st.session_state:
            if st.session_state['rol'] == 'Administrador':
                admin = Administrador()
                admin.mostrarDashboard()
            elif st.session_state['rol'] == 'Gestor Puerta por Puerta':
                gestorPuerta = GestorPuertaPuerta()
                gestorPuerta.mostrarDashboard()
            elif st.session_state['rol'] == 'Gestor Call Center':
                gestorCall = GestorCallCenter()
                gestorCall.mostrarDashboard()

# Ejecutar la aplicación
ejecutarAplicacion()