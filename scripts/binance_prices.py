import requests
import logging
import time
import pandas as pd

# Configuración básica del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_binance_prices(retries=3, backoff_factor=2):
    """
    Obtiene los precios actuales de las criptomonedas desde la API de Binance,
    con reintentos en caso de fallos temporales.

    Args:
        retries (int): Número de intentos de reintento en caso de error.
        backoff_factor (int): Factor de tiempo para aumentar el intervalo entre reintentos.

    Returns:
        list or None: Una lista de diccionarios con el símbolo y el precio de cada criptomoneda, o None si falla.
    """
    url = "https://api.binance.com/api/v3/ticker/price"

    for attempt in range(retries):
        try:
            logging.info(f"Intentando obtener precios de Binance, intento {attempt + 1}/{retries}")
            response = requests.get(url, timeout=10)
            response.raise_for_status() 
            prices = response.json()
            logging.info("Precios obtenidos con éxito de Binance.")
            return prices

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"Error HTTP ocurrido: {http_err}. No se realizará un nuevo intento.")
            break

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as err:
            logging.warning(f"{type(err).__name__}: {err}. Reintentando en {backoff_factor ** attempt} segundos...")
            time.sleep(backoff_factor ** attempt)

        except Exception as err:
            logging.error(f"Ocurrió un error inesperado: {err}. No se realizará un nuevo intento.")
            break

    logging.error("No se pudo obtener los precios después de varios intentos.")
    return None

def save_prices_to_csv(prices, filename='/opt/integrador/datos/binance_prices.csv'):
    """
    Guarda los precios en un archivo CSV.

    Args:
        prices (list): Lista de precios a guardar.
        filename (str): Nombre del archivo CSV.
    """
    try:
        df = pd.DataFrame(prices)
        df.to_csv(filename, index=False)
        logging.info(f"Precios guardados en {filename}")
    except Exception as e:
        logging.error(f"Error al guardar los precios en el archivo CSV: {e}")

if __name__ == "__main__":
    current_prices = get_binance_prices()
    if current_prices:
        save_prices_to_csv(current_prices)

        # Imprimir los precios obtenidos
        for item in current_prices:
            logging.info(f"{item['symbol']}: {item['price']}")
    else:
        logging.error("No se pudieron obtener precios de Binance.")
