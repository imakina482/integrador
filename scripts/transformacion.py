import os
import logging
import pandas as pd

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constantes
FILE_PATH = '/opt/integrador/datos/binance_prices.csv'
REQUIRED_COLUMNS = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume']

def load_data(file_path):
    """Carga el DataFrame desde un archivo CSV.

    Args:
        file_path (str): Ruta del archivo CSV.

    Returns:
        pd.DataFrame: DataFrame cargado desde el archivo CSV.
    """
    if not os.path.exists(file_path):
        logging.error(f"El archivo {file_path} no existe.")
        return None

    try:
        df = pd.read_csv(file_path)
        logging.info(f"Datos cargados exitosamente desde {file_path}")
        return df
    except Exception as e:
        logging.error(f"Error al cargar los datos desde {file_path}: {e}")
        return None

def transform_data(df):
    """Transforma los datos del DataFrame.

    Args:
        df (pd.DataFrame): DataFrame original.

    Returns:
        tuple: DataFrame transformado y DataFrame con cambios positivos.
    """
    # Verificación de columnas necesarias
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        logging.error(f"Las siguientes columnas están ausentes en el DataFrame: {missing_columns}")
        return None, None

    # Selecciono algunas columnas relevantes
    df = df[REQUIRED_COLUMNS]
    df.columns = ['Timestamp', 'Open Price', 'High Price', 'Low Price', 'Close Price', 'Volume']

    # Cambio a tipo float y manejo de NaN
    df[['Open Price', 'High Price', 'Low Price', 'Close Price', 'Volume']] = (
        df[['Open Price', 'High Price', 'Low Price', 'Close Price', 'Volume']]
        .astype(float)
        .fillna(0)
    )

    # Calculo diferencia entre el precio de cierre y apertura
    df['Price Change'] = df.apply(lambda row: calculate_price_difference(row['Open Price'], row['Close Price']), axis=1)

    # Obtengo solo datos de días con cambio de precio positivo
    df_positive_change = df[df['Price Change'] > 0]

    logging.info("Transformación de datos completada.")
    return df, df_positive_change

def calculate_price_difference(open_price, close_price):
    """Calcula la diferencia entre el precio de apertura y cierre.

    Args:
        open_price (float): Precio de apertura.
        close_price (float): Precio de cierre.

    Returns:
        float: Diferencia de precio.
    """
    return close_price - open_price

def main():
    df = load_data(FILE_PATH)
    if df is not None:
        df_transformed, df_positive_change = transform_data(df)
        if df_transformed is not None and df_positive_change is not None:
            # Muestro resultados
            logging.info("DataFrame transformado:")
            logging.info(df_transformed.head())
            logging.info("DataFrame con cambios positivos:")
            logging.info(df_positive_change.head())
        else:
            logging.error("Error en la transformación de datos.")
    else:
        logging.error("No se pudieron cargar los datos.")

if __name__ == "__main__":
    main()
