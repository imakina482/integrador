import requests
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def transform_data():
    """
    Transforma los datos obtenidos de la API de Binance para el par BTCUSDT.

    Returns:
        pd.DataFrame: DataFrame transformado con las columnas adecuadas.
    """
    # URL de la API de Binance para obtener el precio del par de criptomonedas
    url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=100'

    try:
        # Solicitud GET a la API de Binance
        response = requests.get(url)
        response.raise_for_status()

        # Procesar la respuesta
        data = response.json()

        # Crear un DataFrame con los datos relevantes
        df = pd.DataFrame(data, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
                                         'Close Time', 'Quote Asset Volume', 'Number of Trades',
                                         'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume',
                                         'Ignore'])

        logging.info(f"Primeros valores de la columna 'Volume': {df['Volume'].head()}")

        # Convertir las columnas 'Open Time' y 'Close Time' a formato de fecha
        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
        df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')

        # Ajustar las columnas del DataFrame transformado
        transformed_df = pd.DataFrame({
            'timestamp': df['Open Time'],
            'price': df['Close'].astype(float),
            'volume': df['Volume'].astype(float),
            'symbol': 'BTCUSDT',
            'fecha_inicio': df['Open Time'],
            'registro_actual': True
        })

        logging.info("Datos transformados exitosamente.")
        return transformed_df

    except requests.exceptions.RequestException as e:
        logging.error(f"Error en la solicitud a la API de Binance: {e}")
    except Exception as e:
        logging.error(f"Ocurrió un error inesperado: {e}")

    # Retorna un DataFrame vacío en caso de error
    return pd.DataFrame(columns=['timestamp', 'price', 'volume', 'symbol', 'fecha_inicio', 'registro_actual'])

if __name__ == "__main__":
    df = transform_data()
    if not df.empty:
        logging.info("Transformación de datos completada. Primeras filas del DataFrame:")
        logging.info(df.head())
    else:
        logging.error("La transformación de datos no se pudo completar.")
