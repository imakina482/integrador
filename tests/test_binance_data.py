import os
import sys
import unittest
from unittest.mock import patch
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.dataFrame import transform_data

class TestBinanceData(unittest.TestCase):
    
    def setUp(self):
        # Datos simulados para el test
        self.mock_response_data = [
            [1629308400000, '42000.00', '42500.00', '41500.00', '42050.00', '100',
             1629312000000, '42000.00', 50, '50', '50', '0']
        ]

    @patch('scripts.dataFrame.requests.get')
    def test_transform_data_success(self, mock_get):      
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.mock_response_data        
    
        df = transform_data()
        
        # Verificaciones básicas
        self.assertIsInstance(df, pd.DataFrame, "El resultado debe ser un DataFrame")
        self.assertFalse(df.empty, "El DataFrame no debería estar vacío")
        self.assertEqual(len(df), 1, "El DataFrame debería tener una fila")
        
        # Verificaciones de columnas
        expected_columns = ['timestamp', 'price', 'volume', 'symbol', 'fecha_inicio', 'registro_actual']
        self.assertListEqual(list(df.columns), expected_columns, "Las columnas no coinciden con las esperadas")
        
        # Verifica el contenido
        self.assertEqual(df['fecha_inicio'][0], pd.to_datetime(1629308400000, unit='ms'), "El valor de 'fecha_inicio' no es el esperado")
        self.assertEqual(df['price'][0], 42050.00, "El precio no es el esperado")
        self.assertEqual(df['volume'][0], 100.0, "El volumen no es el esperado")
        self.assertEqual(df['symbol'][0], 'BTCUSDT', "El símbolo no es el esperado")
        self.assertTrue(df['registro_actual'][0], "El registro_actual debería ser True")

    @patch('scripts.dataFrame.requests.get')
    def test_transform_data_failure(self, mock_get):
        # Configurar el mock para que devuelva un error
        mock_get.return_value.status_code = 500        
  
        df = transform_data()
        
        # Verificar que el DataFrame esté vacío
        self.assertIsInstance(df, pd.DataFrame, "El resultado debe ser un DataFrame")
        self.assertTrue(df.empty, "El DataFrame debería estar vacío cuando la solicitud falla")

if __name__ == '__main__':
    unittest.main()
