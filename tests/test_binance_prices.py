import unittest
from unittest.mock import patch
import requests   
from binance_prices import get_binance_prices
import logging

class TestGetBinancePrices(unittest.TestCase):
    @patch('binance_prices.requests.get') 
    def test_get_binance_prices_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {'symbol': 'BTCUSDT', 'price': '42000.00'},
            {'symbol': 'ETHUSDT', 'price': '3000.00'}
        ]
        
        prices = get_binance_prices()
        
        self.assertIsInstance(prices, list)
        self.assertGreater(len(prices), 0)
        self.assertEqual(prices[0]['symbol'], 'BTCUSDT')

    @patch('binance_prices.requests.get')
    def test_get_binance_prices_http_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError("404 Client Error: Not Found for url")

        with self.assertLogs(level='ERROR') as log:
            prices = get_binance_prices()
        
        self.assertIsNone(prices)
        self.assertIn("HTTP error occurred: 404 Client Error: Not Found for url", log.output[0])

if __name__ == '__main__':
    unittest.main()
