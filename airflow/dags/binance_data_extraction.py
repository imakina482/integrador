from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

# Cargo las variables de entorno desde el archivo .env
load_dotenv()

def run_binance_script():
    # Verifica si el directorio 'datos' existe, si no, lo crea
    if not os.path.exists('datos'):
        os.makedirs('datos')

    result = subprocess.run(
        ['python', '/opt/airflow/binance_prices.py'],  # Cambia la ruta aquí
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print("stdout:", result.stdout.decode())
    print("stderr:", result.stderr.decode())

def connect_to_redshift():
    try:
        connection = psycopg2.connect(
            host=os.getenv('REDSHIFT_HOST'),
            dbname=os.getenv('REDSHIFT_DBNAME'),
            user=os.getenv('REDSHIFT_USER'),
            password=os.getenv('REDSHIFT_PASSWORD'),
            port=os.getenv('REDSHIFT_PORT')
        )
        print("Conexión exitosa a Redshift")
        return connection
    except Exception as e:
        print(f"Error al conectarse a Redshift: {e}")
        return None

def load_data_to_redshift():
    connection = connect_to_redshift()
    if connection is None:
        return

    try:
        df = pd.read_csv('datos/binance_prices.csv')
        cursor = connection.cursor()
        current_time = datetime.utcnow()

        for index, row in df.iterrows():
            symbol = row['symbol']
            price = row['price']

            # 1. Verificar si el registro ya existe y está activo
            cursor.execute("""
                SELECT * FROM 2024_paola_torrealba_schema.binance
                WHERE symbol = %s AND registro_actual = TRUE;
            """, (symbol,))
            existing_record = cursor.fetchone()

            if existing_record:
                # Si el precio ha cambiado
                if existing_record[1] != price:
                    # 2. Desactiva el registro anterior
                    cursor.execute("""
                        UPDATE 2024_paola_torrealba_schema.binance
                        SET fecha_fin = %s, registro_actual = FALSE
                        WHERE symbol = %s AND registro_actual = TRUE;
                    """, (current_time, symbol))

                    # 3. Inserta el nuevo registro con el nuevo precio
                    cursor.execute("""
                        INSERT INTO 2024_paola_torrealba_schema.binance (symbol, price, fecha_inicio, registro_actual)
                        VALUES (%s, %s, %s, TRUE);
                    """, (symbol, price, current_time))
            else:
                # 4. Si no existe, insertar un nuevo registro
                cursor.execute("""
                    INSERT INTO 2024_paola_torrealba_schema.binance (symbol, price, fecha_inicio, registro_actual)
                    VALUES (%s, %s, %s, TRUE);
                """, (symbol, price, current_time))

        connection.commit()
        print("Datos insertados o actualizados exitosamente en Redshift.")

    except Exception as e:
        print(f"Error al insertar o actualizar datos en Redshift: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 13),
    'retries': 1,
}

with DAG('binance_data_extraction',
         default_args=default_args,
         schedule='@daily',
         catchup=False) as dag:

    run_script = PythonOperator(
        task_id='run_binance_script',
        python_callable=run_binance_script,
    )

    load_data = PythonOperator(
        task_id='load_data_to_redshift',
        python_callable=load_data_to_redshift,
    )

    run_script >> load_data
