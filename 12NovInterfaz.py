import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cargar el archivo CSV
@st.cache_data  # Cache para mejorar el rendimiento al recargar datos
def cargarDatos():
    return pd.read_csv('vendedores.csv')

# Llamar a la función para cargar datos
datosOriginales = cargarDatos()  # Guardamos los datos originales sin filtrar

# Título principal de la aplicación
st.title("Análisis de Vendedores")

# Filtro por región
# Crear un contenedor para los filtros
with st.container():
    st.subheader("Filtro por Región")
    regiones = datosOriginales['REGION'].unique()
    regionSeleccionada = st.selectbox("Selecciona una región", ["Todas"] + list(regiones))

    # Filtrar los datos por región seleccionada solo para la tabla
    if regionSeleccionada != "Todas":
        datosFiltrados = datosOriginales[datosOriginales['REGION'] == regionSeleccionada]
    else:
        datosFiltrados = datosOriginales

# Mostrar tabla de datos filtrados
st.write("Tabla de Datos")
st.dataframe(datosFiltrados)

# Gráficas de Unidades Vendidas, Ventas Totales y Porcentajes de Ventas (usando datos sin filtrar)
with st.container():
    st.subheader("Gráficas de Ventas")

    # Unidades Vendidas por Región
    st.write("Unidades Vendidas por Región")
    figUnidades, ax = plt.subplots()
    datosOriginales.groupby('REGION')['UNIDADES VENDIDAS'].sum().plot(kind='bar', ax=ax)
    ax.set_ylabel("Unidades Vendidas")
    st.pyplot(figUnidades)

    # Ventas Totales por Región
    st.write("Ventas Totales por Región")
    figVentas, ax = plt.subplots()
    datosOriginales.groupby('REGION')['VENTAS TOTALES'].sum().plot(kind='bar', ax=ax)
    ax.set_ylabel("Ventas Totales")
    st.pyplot(figVentas)

    # Porcentaje de Ventas por Región
    st.write("Porcentaje de Ventas por Región")
    ventasTotales = datosOriginales['VENTAS TOTALES'].sum()
    datosOriginales['PORCENTAJE VENTAS'] = (datosOriginales['VENTAS TOTALES'] / ventasTotales) * 100
    figPorcentaje, ax = plt.subplots()
    datosOriginales.groupby('REGION')['PORCENTAJE VENTAS'].sum().plot(kind='pie', ax=ax, autopct='%1.1f%%')
    ax.set_ylabel("")
    st.pyplot(figPorcentaje)

# Selección de un vendedor específico (también usando datos sin filtrar)
with st.container():
    st.subheader("Buscar Información de un Vendedor")
    # Obtener la lista de vendedores
    vendedores = datosOriginales['NOMBRE'].unique()
    vendedorSeleccionado = st.selectbox("Selecciona un Vendedor", vendedores)

    # Filtrar datos para el vendedor seleccionado
    datosVendedor = datosOriginales[datosOriginales['NOMBRE'] == vendedorSeleccionado]
    
    # Mostrar información del vendedor
    st.write("Información del Vendedor Seleccionado")
    st.dataframe(datosVendedor)
