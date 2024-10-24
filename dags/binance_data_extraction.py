import os
import logging
import subprocess
from datetime import datetime
from dotenv import load_dotenv

from airflow import DAG
from airflow.operators.python import PythonOperator
from binance_prices import get_binance_prices
from process_data import process_binance_data
from enrich_data import fetch_prices
from convert_to_parquet import convert_csv_to_parquet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def run_binance_script():
    """
    Ejecuta el script binance_prices.py y captura su salida.
    Crea la carpeta 'datos' si no existe.
    """
    datos_dir = '/opt/integrador/datos'
    if not os.path.exists(datos_dir):
        os.makedirs(datos_dir)
        logging.info(f"Carpeta creada: {datos_dir}")

    try:
        result = subprocess.run(
            ['python', '/opt/integrador/scripts/binance_prices.py'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logging.info(f"Script ejecutado exitosamente: {result.stdout.decode()}")
        if result.stderr:
            logging.warning(f"Advertencias durante la ejecución del script: {result.stderr.decode()}")
    except subprocess.CalledProcessError as err:
        logging.error(f"Error al ejecutar el script binance_prices.py: {err}")
    except Exception as e:
        logging.error(f"Error inesperado al ejecutar el script binance_prices.py: {e}")

def connect_to_redshift():
    """
    Verifica la conexión a la base de datos Redshift.
    """
    from psycopg2 import connect

    try:
        connection = connect(
            host=os.getenv('REDSHIFT_HOST'),
            dbname=os.getenv('REDSHIFT_DBNAME'),
            user=os.getenv('REDSHIFT_USER'),
            password=os.getenv('REDSHIFT_PASSWORD'),
            port=os.getenv('REDSHIFT_PORT')
        )
        logging.info("Conexión exitosa a Redshift")
        return connection
    except Exception as e:
        logging.error(f"Error al conectar a Redshift: {e}")
        return None

def verify_redshift_connection():
    """
    Verifica la conexión a Redshift y cierra la conexión si es exitosa.
    """
    connection = connect_to_redshift()
    if connection:
        logging.info("La conexión a Redshift fue exitosa. La carga de datos se gestionará desde Streamlit.")
        connection.close()
    else:
        logging.error("Falló la conexión a Redshift.")

# Configuración del DAG de Airflow
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 13),
    'retries': 1,
}

with DAG(
    'binance_data_extraction',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    run_script_task = PythonOperator(
        task_id='run_binance_script',
        python_callable=run_binance_script,
    )

    process_data_task = PythonOperator(
        task_id='process_binance_data',
        python_callable=process_binance_data,
    )

    enrich_data_task = PythonOperator(
        task_id='fetch_price',
        python_callable=fetch_prices,
    )
    convert_to_parquet_task = PythonOperator(
        task_id='convert_to_parquet',
        python_callable=convert_csv_to_parquet,
    )
    verify_connection_task = PythonOperator(
        task_id='verify_redshift_connection',
        python_callable=verify_redshift_connection,
    )

    run_script_task >> process_data_task >> enrich_data_task >> convert_to_parquet_task >> verify_connection_task

