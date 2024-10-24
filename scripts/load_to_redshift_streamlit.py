import os
import logging
import pandas as pd
import streamlit as st
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
            connection.execute(text(create_table_query))
        logging.info("La tabla 'binance' ha sido creada (si no existía).")
    except Exception as e:
        logging.error(f"Error al crear la tabla: {e}")

def load_data_to_redshift(df: pd.DataFrame, engine) -> None:
    """
    Carga los datos de un DataFrame a la tabla en Redshift, manejando valores NaN y asegurando que las columnas necesarias estén presentes.
    """
    try:

        required_columns = ['timestamp', 'price', 'symbol']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logging.error(f"Las siguientes columnas están ausentes en el archivo: {missing_columns}")
            st.error(f"Las siguientes columnas están ausentes en el archivo: {missing_columns}")
            return

        if 'volume' not in df.columns:
            df['volume'] = 0 

        # Reemplazo NaN en la columna 'volume' por 0
        df['volume'] = df['volume'].fillna(0)

        # Ajustolos datos para que coincidan con el esquema de la tabla
        df['fecha_inicio'] = pd.to_datetime('now')
        df['fecha_fin'] = None
        df['registro_actual'] = True

        df = df[['timestamp', 'price', 'volume', 'symbol', 'fecha_inicio', 'fecha_fin', 'registro_actual']]

        with engine.connect() as connection:
            for _, row in df.iterrows():
                # Verifico si el registro ya existe y está activo
                existing_record = connection.execute(text("""
                    SELECT * FROM "2024_paola_torrealba_schema".binance 
                    WHERE symbol = :symbol AND registro_actual = TRUE;
                """), {"symbol": row['symbol']}).fetchone()

                if existing_record and existing_record[1] != row['price']:
                    # Desactivo el anterior
                    connection.execute(text("""
                        UPDATE "2024_paola_torrealba_schema".binance 
                        SET fecha_fin = :fecha_fin, registro_actual = FALSE 
                        WHERE symbol = :symbol AND registro_actual = TRUE;
                    """), {"fecha_fin": row['fecha_inicio'], "symbol": row['symbol']})

                # Inserto uno nuevo
                connection.execute(text("""
                    INSERT INTO "2024_paola_torrealba_schema".binance (timestamp, price, volume, symbol, fecha_inicio, fecha_fin, registro_actual)
                    VALUES (:timestamp, :price, :volume, :symbol, :fecha_inicio, NULL, TRUE);
                """), {
                    "timestamp": row['timestamp'], 
                    "price": row['price'], 
                    "volume": row['volume'], 
                    "symbol": row['symbol'], 
                    "fecha_inicio": row['fecha_inicio']
                })

        logging.info("Datos insertados o actualizados exitosamente en Redshift.")
        st.success("Datos cargados exitosamente en Redshift.")

    except Exception as e:
        logging.error(f"Error al insertar o actualizar datos en Redshift: {e}")
        st.error(f"Error al cargar datos en Redshift: {e}")

st.title("Carga de Datos a Redshift")

file_type = st.radio("Selecciona el tipo de archivo", ('CSV', 'Parquet'))

uploaded_file = st.file_uploader(f"Sube el archivo {file_type.lower()}", type=["csv", "parquet"])

if uploaded_file is not None:
    if file_type == 'CSV':
        df = pd.read_csv(uploaded_file)
    elif file_type == 'Parquet':
        df = pd.read_parquet(uploaded_file)

    st.write("Vista previa del archivo:")
    st.dataframe(df.head())

    # Conecto a Redshift y creo la tabla si no existe
    engine = connect_to_redshift()
    if engine:
        create_table_if_not_exists(engine)

        # Cargolos datos a Redshift
        if st.button("Cargar a Redshift"):
            load_data_to_redshift(df, engine)
