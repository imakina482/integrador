import os
import logging
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_redshift():
    """
    Establece una conexión a la base de datos Redshift.

    Returns:
        connection: Objeto de conexión a Redshift si la conexión es exitosa, None en caso de error.
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv('REDSHIFT_HOST'),
            dbname=os.getenv('REDSHIFT_DBNAME'),
            user=os.getenv('REDSHIFT_USER'),
            password=os.getenv('REDSHIFT_PASSWORD'),
            port=os.getenv('REDSHIFT_PORT')
        )
        logging.info("Conexión exitosa a Redshift")
        return connection
    except psycopg2.OperationalError as op_err:
        logging.error(f"Error operacional al conectarse a Redshift: {op_err}")
        return None
    except Exception as e:
        logging.error(f"Error inesperado al conectarse a Redshift: {e}")
        return None

def insert_record():
    """
    Inserta un registro en la tabla 'binance' de Redshift.
    """
    connection = connect_to_redshift()
    if connection:
        current_time = datetime.now()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO "2024_paola_torrealba_schema".binance (symbol, price, fecha_inicio, timestamp, registro_actual)
                    VALUES (%s, %s, %s, %s, %s);
                """, ('BTC', 30000, current_time, current_time, True))
                connection.commit()
                logging.info("Registro insertado manualmente en la tabla 'binance'.")
        except Exception as e:
            logging.error(f"Error al insertar el registro: {e}")
        finally:
            connection.close()

def test_query():
    """
    Ejecuta una consulta de prueba para contar el número de registros en la tabla 'binance'.
    """
    connection = connect_to_redshift()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) FROM "2024_paola_torrealba_schema".binance;')
                count = cursor.fetchone()[0]
                logging.info(f"Número de registros en la tabla 'binance': {count}")
        except Exception as e:
            logging.error(f"Error al ejecutar la consulta: {e}")
        finally:
            connection.close()

if __name__ == "__main__":
    test_query()
    insert_record()
