import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_redshift():
    """
    Crea una conexión a la base de datos Redshift usando SQLAlchemy.
    """
    try:
        connection_string = f'redshift+psycopg2://{os.getenv("REDSHIFT_USER")}:{os.getenv("REDSHIFT_PASSWORD")}@{os.getenv("REDSHIFT_HOST")}:{os.getenv("REDSHIFT_PORT")}/{os.getenv("REDSHIFT_DBNAME")}'
        engine = create_engine(connection_string)
        logging.info("Conexión exitosa a Redshift")
        return engine
    except Exception as e:
        logging.error(f"Error al conectar a Redshift: {e}")
        return None

def create_table_if_not_exists(engine):
    """
    Crea la tabla en Redshift si no existe.
    """
    table_exists_query = """
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = '2024_paola_torrealba_schema'
    AND table_name = 'binance';
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS "2024_paola_torrealba_schema".binance (
        timestamp TIMESTAMP NOT NULL,
        price FLOAT NOT NULL,
        volume FLOAT,
        symbol VARCHAR(10) NOT NULL,
        fecha_inicio TIMESTAMP NOT NULL,
        fecha_fin TIMESTAMP,
        registro_actual BOOLEAN NOT NULL DEFAULT TRUE,
        PRIMARY KEY (symbol, fecha_inicio)
    );
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text(table_exists_query)).fetchone()
            if result:
                logging.info("La tabla 'binance' ya existe, no se requiere creación.")
            else:
                connection.execute(text(create_table_query))
                logging.info("La tabla 'binance' ha sido creada.")
    except Exception as e:
        logging.error(f"Error al crear la tabla: {e}")

def load_data_to_redshift(df: pd.DataFrame, engine):
    """
    Carga los datos de un DataFrame a la tabla en Redshift.
    """
    try:     
        required_columns = ['price', 'symbol']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logging.error(f"Las siguientes columnas están ausentes en el archivo: {missing_columns}")
            return

        # Agregar la columna 'timestamp' con la fecha y hora actual si no existe
        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.to_datetime('now')

        # Agregar la columna 'volume' si no existe
        if 'volume' not in df.columns:
            df['volume'] = 0

        # Asegurar que las columnas 'fecha_inicio' y 'fecha_fin' estén presentes y configuradas
        df['fecha_inicio'] = pd.to_datetime('now') if 'fecha_inicio' not in df.columns else pd.to_datetime(df['fecha_inicio'])
        df['fecha_fin'] = None if 'fecha_fin' not in df.columns else df['fecha_fin'].apply(lambda x: None if pd.isna(x) or x == 0 else x)
        df['registro_actual'] = True

        # Seleccionar las columnas en el orden esperado
        df = df[['timestamp', 'price', 'volume', 'symbol', 'fecha_inicio', 'fecha_fin', 'registro_actual']]

        # Realizar la inserción o actualización en Redshift
        with engine.connect() as connection:
            for _, row in df.iterrows():
                existing_record = connection.execute(text("""
                    SELECT * FROM "2024_paola_torrealba_schema".binance 
                    WHERE symbol = :symbol AND registro_actual = TRUE;
                """), {"symbol": row['symbol']}).fetchone()

                if existing_record and existing_record[1] != row['price']:
                    connection.execute(text("""
                        UPDATE "2024_paola_torrealba_schema".binance 
                        SET fecha_fin = :fecha_fin, registro_actual = FALSE 
                        WHERE symbol = :symbol AND registro_actual = TRUE;
                    """), {"fecha_fin": row['fecha_inicio'], "symbol": row['symbol']})

                connection.execute(text("""
                    INSERT INTO "2024_paola_torrealba_schema".binance (timestamp, price, volume, symbol, fecha_inicio, fecha_fin, registro_actual)
                    VALUES (:timestamp, :price, :volume, :symbol, :fecha_inicio, :fecha_fin, :registro_actual);
                """), {
                    "timestamp": row['timestamp'],
                    "price": row['price'],
                    "volume": row['volume'],
                    "symbol": row['symbol'],
                    "fecha_inicio": row['fecha_inicio'],
                    "fecha_fin": row['fecha_fin'],
                    "registro_actual": row['registro_actual']
                })

        logging.info("Datos insertados o actualizados exitosamente en Redshift.")
    except Exception as e:
        logging.error(f"Error al insertar o actualizar datos en Redshift: {e}")


if __name__ == "__main__":
    engine = connect_to_redshift()
    if engine:
        create_table_if_not_exists(engine)
