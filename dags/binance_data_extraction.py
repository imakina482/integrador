import os
import logging
import subprocess
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from airflow import DAG
from airflow.operators.python import PythonOperator
from binance_prices import get_binance_prices
from process_data import process_binance_data
from enrich_data import fetch_prices
from convert_to_parquet import convert_csv_to_parquet
from load_to_redshift import connect_to_redshift, create_table_if_not_exists, load_data_to_redshift

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def run_binance_script():
    """
    Ejecuta el script binance_prices.py y captura su salida.
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

def verify_redshift_connection():
    """
    Verifica la conexión a Redshift.
    """
    engine = connect_to_redshift()
    if engine:
        logging.info("Conexión exitosa a Redshift.")
        engine.dispose()
    else:
        logging.error("Falló la conexión a Redshift.")

def load_data_to_redshift_task():
    """
    Tarea que carga los datos en Redshift.
    """
    try:
        # Cargar el archivo CSV como DataFrame
        df = pd.read_csv('/opt/integrador/datos/enriched_data.csv')

        # Conectar a Redshift
        engine = connect_to_redshift()

        if engine:
            # Crear la tabla si no existe
            create_table_if_not_exists(engine)
            # Cargar los datos a Redshift
            load_data_to_redshift(df, engine)
            engine.dispose()
            logging.info("Datos cargados exitosamente a Redshift.")
        else:
            logging.error("No se pudo conectar a Redshift.")
    except Exception as e:
        logging.error(f"Error en la tarea de carga a Redshift: {e}")

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

    load_data_to_redshift_op = PythonOperator(
        task_id='load_data_to_redshift',
        python_callable=load_data_to_redshift_task,
    )

    run_script_task >> process_data_task >> enrich_data_task >> convert_to_parquet_task >> verify_connection_task >> load_data_to_redshift_op
