import requests
import pandas as pd
import time
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Cargar las variables de entorno del archivo .env
load_dotenv()
COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY')

# Crear la carpeta 'datos' si no existe
if not os.path.exists('datos'):
    os.makedirs('datos')

# Configuraciones de la API de CoinMarketCap
BASE_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
}

# Lista de criptomonedas a consultar
cryptocurrencies = [
    "BTC",  # Bitcoin
    "ETH",  # Ethereum
    "BNB",  # Binance Coin
    "ADA",  # Cardano
    "SOL",  # Solana
    "XRP",  # Ripple
    "DOT",  # Polkadot
    "DOGE", # Dogecoin
    "LTC",  # Litecoin
    "LINK", # Chainlink
    "MATIC", # Polygon
    "SHIB",  # Shiba Inu
    "TRX",  # TRON
    "AVAX", # Avalanche
    "FTM",  # Fantom
    "NEAR"  # NEAR Protocol
]

# Caché para almacenar los precios temporalmente
cache = {}
cache_expiration = 60 

def fetch_prices():
    """
    Obtiene los precios actuales de las criptomonedas especificadas utilizando la API de CoinMarketCap.
    La función almacena temporalmente los precios en caché para evitar consultas repetidas en un corto tiempo.
    Si el precio de una criptomoneda está en caché y no ha expirado, se reutiliza el valor en lugar de hacer una nueva solicitud.
    Los precios obtenidos se guardan en un archivo CSV en la carpeta 'datos'.

    Returns:
        None
    """
    prices = []
    current_time = time.time()

    for symbol in cryptocurrencies:
        # Verificar si el precio está en caché y si aún es válido
        if symbol in cache and current_time - cache[symbol]['timestamp'] < cache_expiration:
            price = cache[symbol]['price']
            logging.info(f"Usando el precio en caché para {symbol}: {price}")
        else:
            # Construir los parámetros de la solicitud
            parameters = {
                'symbol': symbol,
                'convert': 'USD'
            }

            try:
                # Hacer la solicitud a la API de CoinMarketCap
                response = requests.get(BASE_URL, headers=headers, params=parameters)
                response.raise_for_status() 
                data = response.json()

                # Extraer el precio de la respuesta de la API
                price = data['data'][symbol]['quote']['USD']['price']
                logging.info(f"Precio obtenido para {symbol}: {price}")

                # Almacenar en caché
                cache[symbol] = {'price': price, 'timestamp': current_time}

            except requests.exceptions.HTTPError as http_err:
                logging.error(f"Error HTTP al obtener el precio de {symbol}: {http_err}")
                continue
            except KeyError:
                logging.error(f"No se pudo encontrar el precio para {symbol}.")
                continue
            except Exception as e:
                logging.error(f"Error al hacer la solicitud para {symbol}: {e}")
                continue
        
        # Agregar el precio a la lista
        prices.append({'symbol': symbol, 'price': price, 'timestamp': datetime.now()})

    # Guardar los precios en un DataFrame y luego en un archivo CSV
    try:
        df = pd.DataFrame(prices)
        df.to_csv('/opt/integrador/datos/crypto_prices.csv', mode='a', header=False, index=False)
        logging.info("Precios guardados exitosamente en /opt/integrador/datos/crypto_prices.csv")
    except Exception as e:
        logging.error(f"Error al guardar los precios en el archivo CSV: {e}")

if __name__ == "__main__":
    fetch_prices()
