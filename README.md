# TP integrador

Este proyecto tiene como objetivo procesar y cargar datos de criptomonedas obtenidos de la API de Binance en una base de datos Redshift.
También permite enriquecer los datos con información adicional de CoinMarketCap y visualizar los resultados mediante una aplicación en Streamlit.

# Scripts Principales
- Extracción de datos desde Binance: Obtención de precios de criptomonedas.
- Enriquecimiento de datos: Integración de información adicional de CoinMarketCap.
- Carga en Redshift: La carga de datos en la base de datos se realiza manualmente.
- Automatización de pruebas: Pruebas unitarias para verificar la funcionalidad de los scripts.
  
# Clonar el repositorio:
git clone https://TOKEN@github.com/imakina482/integrador.git
cd integrador

# Levantar el proyecto:
Crear un entorno virtual con Python 3.8:
python3.8 -m venv venv
source venv/bin/activate

Instalar las dependencias desde requirements.txt:
pip install -r requirements.txt

Instalar manualmente pandas y Airflow:
pip install pandas==1.5.3 apache-airflow==2.10.1

Ejecutar el proyecto con Docker Compose:
docker-compose up

Para detener los servicios usar:
docker-compose down

# Scripts Principales
- binance_prices.py: Extrae los precios de criptomonedas desde Binance y los guarda en un archivo CSV.
- enriched_data.py: Enriquece los datos extraídos con información adicional de CoinMarketCap.
- dataFrame.py: Realiza transformaciones en los datos para adaptarlos al esquema de la base de datos.

# Carga Manual en la Base de Datos
Los datos se cargan en la base de datos Redshift manualmente utilizando streamlite. La tabla principal en Redshift es "binance"
y tiene las sigueintes columnas :

timestamp: Marca de tiempo.
price: Precio de la criptomoneda en el momento registrado.
volume: Cantidad total de la criptomoneda negociada en el periodo de tiempo registrado.
symbol: Símbolo de la criptomoneda (por ejemplo, BTCUSDT).
fecha_inicio: Fecha y hora de inicio del registro.
fecha_fin: Fecha y hora de finalización del registro (puede usarse para indicar la validez temporal de los datos).
registro_actual: Indicador que muestra si el registro es el más reciente (True) o si ha sido superado por uno más nuevo.

![image](https://github.com/user-attachments/assets/9a15a0c1-fec8-43c3-b8a0-84377e313868)

# Ejecución de Streamlit
Para levantar la aplicación de Streamlit con las dos opciones de visualización:

 streamlit run scripts/load_to_redshift_streamlit.py 

#  Ejecutar las pruebas:
 python -m unittest discover -v tests/

Pipeline de CI/CD
El proyecto usa GitHub Actions para la integración continua, con los siguientes pasos:

Instalación de dependencias: Las dependencias principales están en requirements.txt, pero algunas (pandas y Airflow) se instalan manualmente ya que tardan más.
Ejecución de pruebas: Se ejecutan las pruebas unitarias en cada push o pull request.
