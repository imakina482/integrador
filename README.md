# TP integrador 

Este proyecto tiene como objetivo procesar y cargar datos de criptomonedas obtenidos de la API de Binance en una base de datos Redshift.
También permite enriquecer los datos con información adicional de CoinMarketCap y visualizar los resultados mediante una aplicación en Streamlit.

# Scripts Principales
- Extracción de datos desde Binance: Obtención de precios de criptomonedas.
- Enriquecimiento de datos: Integración de información adicional de CoinMarketCap.
- Carga en Redshift: La carga de datos en la base de datos se realiza manualmente.
- Automatización de pruebas: Pruebas unitarias para verificar la funcionalidad de los scripts.
  
# Clonar el repositorio:
`git clone https://TOKEN@github.com/imakina482/integrador.git`
`cd integrador`

# Levantar el proyecto:
Crear un entorno virtual con Python 3.8:
python3.8 -m venv venv
source venv/bin/activate

Instalar las dependencias desde requirements.txt:
`pip install -r requirements.txt`
    

Instalar manualmente pandas y Airflow:
`pip install pandas==1.5.3 apache-airflow==2.10.1`

Ejecutar el proyecto con Docker Compose:
`docker-compose up`

Para detener los servicios usar:
`docker-compose down`

# Scripts Principales
- binance_prices.py: Extrae los precios de criptomonedas desde Binance y los guarda en un archivo CSV.
- enriched_data.py: Enriquece los datos extraídos con información adicional de CoinMarketCap.
- dataFrame.py: Realiza transformaciones en los datos para adaptarlos al esquema de la base de datos.

# Carga Manual en la Base de Datos
Los datos se cargan en la base de datos Redshift manualmente utilizando streamlite. La tabla principal en Redshift es "binance"
y tiene las sigueintes columnas :

1. timestamp: Marca de tiempo.
2. price: Precio de la criptomoneda en el momento registrado.
3. volume: Cantidad total de la criptomoneda negociada en el periodo de tiempo registrado.
4. symbol: Símbolo de la criptomoneda (por ejemplo, BTCUSDT).
5. fecha_inicio: Fecha y hora de inicio del registro.
6. fecha_fin: Fecha y hora de finalización del registro (puede usarse para indicar la validez temporal de los datos).
7. registro_actual: Indicador que muestra si el registro es el más reciente (True) o si ha sido superado por uno más nuevo.

![image](https://github.com/user-attachments/assets/9a15a0c1-fec8-43c3-b8a0-84377e313868)

# Airflow-webserver
  http://localhost:8082/
  ![imagen](https://github.com/user-attachments/assets/3dd4ba9d-da38-4ea9-8911-cc7fbd4df5fb)

# Ejecución de Streamlit
Para levantar la aplicación de Streamlit con las dos opciones de visualización:

`streamlit run scripts/load_to_redshift_streamlit.py` 

![image](https://github.com/user-attachments/assets/c20d9a87-6591-432d-8dc3-d048a722f085)

#  Ejecutar las pruebas:
`python -m unittest discover -v tests/`

Pipeline de CI/CD
El proyecto usa GitHub Actions para la integración continua, con los siguientes pasos:

Instalación de dependencias: Las dependencias principales están en requirements.txt, pero algunas (pandas y Airflow) se instalan manualmente ya que tardan más.
Ejecución de pruebas: Se ejecutan las pruebas unitarias en cada push o pull request.

# Automatización de ambiente con makefile
El proyecto incluye un Makefile para automatizar los pasos de configuración:

Configurar el entorno y las dependencias:
`make all`
Esto creará el entorno virtual venv 

Instalar las dependencias desde requirements.txt
`make install_deps` 

Instalar dependencias adicionales (pandas y Airflow) manualmente.
`make install_manual_deps` 

Levantar el proyecto con Docker Compose:
`make docker_up`

Detener los servicios de Docker Compose:
`make docker_down`

Ejecutar las pruebas:
`make test`

Limpiar el entorno eliminando el entorno virtual:
`make clean`

Levantar streamLite:
`make streamlit_up`

Además, el Makefile verifica automáticamente si el archivo .env existe antes de realizar cualquier configuración. 
Si no está presente, muestra un mensaje de error.
