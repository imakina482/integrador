from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess


def run_binance_script():
    subprocess.run(['python', './binance_prices.py'], check=True)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 12),  
    'retries': 1,
}


with DAG('binance_data_extraction',
         default_args=default_args,
         schedule_interval='@daily',  
         catchup=False) as dag:

   
    run_script = PythonOperator(
        task_id='run_binance_script',
        python_callable=run_binance_script,
    )

    run_script  