import requests
import logging
import time
import pandas as pd

def get_binance_prices(retries=3, backoff_factor=2):
    """
    Obtiene los precios actuales de las criptomonedas desde la API de Binance,
    con reintentos en caso de fallos temporales.

    Args:
        retries (int): Número de intentos de reintento en caso de error.
        backoff_factor (int): Factor de tiempo para aumentar el intervalo entre reintentos.

    Returns:
        list: Una lista de diccionarios que contienen el símbolo y el precio de cada criptomoneda.
    """
    url = "https://api.binance.com/api/v3/ticker/price"

    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()

            prices = response.json()
            return prices

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"Error HTTP ocurrido: {http_err}")
            break 

        except requests.exceptions.ConnectionError as conn_err:
            logging.warning(f"Error de conexión: {conn_err}. Reintentando en {backoff_factor ** attempt} segundos...")
            time.sleep(backoff_factor ** attempt)  

        except requests.exceptions.Timeout as timeout_err:
            logging.warning(f"Tiempo de espera agotado: {timeout_err}. Reintentando en {backoff_factor ** attempt} segundos...")
            time.sleep(backoff_factor ** attempt)

        except Exception as err:
            logging.error(f"Ocurrió un error inesperado: {err}")
            break  
    logging.error("No se pudo obtener los precios después de varios intentos.")
    return None

if __name__ == "__main__":
    current_prices = get_binance_prices()
    if current_prices:
        df = pd.DataFrame(current_prices)
        df.to_csv('datos/binance_prices.csv', index=False)
        print("Precios guardados en datos/binance_prices.csv")

        for item in current_prices:
            print(f"{item['symbol']}: {item['price']}")
