import requests
import pandas as pd

def transform_data():
    # URL de la API de Binance para obtener el precio del par de criptomonedas
    url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=100'

    # GET
    response = requests.get(url)

    if response.status_code == 200:  
        data = response.json()

        # Creo un DF con los datos
        df = pd.DataFrame(data, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 
                                         'Close Time', 'Quote Asset Volume', 'Number of Trades', 
                                         'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 
                                         'Ignore'])

        # Convierto la columna 'Open Time' y 'Close Time' a formato de fecha
        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
        df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')

        # Retorno el DataFrame
        return df
    else:
        print("Error en la solicitud:", response.status_code)
        return None
