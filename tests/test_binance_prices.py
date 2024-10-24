import os
import sys
import unittest
from unittest.mock import patch
import requests
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.binance_prices import get_binance_prices

class TestGetBinancePrices(unittest.TestCase):

    @patch('scripts.binance_prices.requests.get')
    def test_get_binance_prices_timeout_error(self, mock_get):
        """
        Prueba que la función maneje correctamente un error de tiempo de espera.
        """
        mock_get.side_effect = requests.exceptions.Timeout("The request timed out")

        # Capturar el log
        with self.assertLogs(level='WARNING') as log:
            prices = get_binance_prices()
        
        # Verifico que el resultado sea None y que se haya registrado el error
        self.assertIsNone(prices, "Debería retornar None en caso de timeout")
        self.assertIn("The request timed out", log.output[0], "Debería registrar un tiempo de espera agotado")

if __name__ == '__main__':
    unittest.main()
