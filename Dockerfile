# usa una imagen base de python compatible
FROM python:3.12-slim

# establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# copia el archivo requirements.txt desde el escritorio al contenedor
COPY requirements.txt /app/requirements.txt

# instala las dependencias desde el archivo
RUN pip install --no-cache-dir -r requirements.txt

# copia tu aplicación al contenedor
COPY . /app

# comando por defecto para ejecutar la aplicación
CMD ["streamlit", "run", "16NovApp.py", "--server.port=8501", "--server.address=0.0.0.0"]
