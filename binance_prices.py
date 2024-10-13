import requests

def get_binance_prices():
    """
    Obtiene los precios actuales de las criptomonedas desde la API de Binance.

    Returns:
        list: Una lista de diccionarios que contienen el símbolo y el precio de cada criptomoneda.
    """
    url = "https://api.binance.com/api/v3/ticker/price"
    
    try:
        response = requests.get(url)
        response.raise_for_status()

        prices = response.json()
        return prices
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


if __name__ == "__main__":
    current_prices = get_binance_prices()
    if current_prices:
        for item in current_prices:
            print(f"{item['symbol']}: {item['price']}")
