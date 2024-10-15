import unittest
from unittest.mock import patch
from scripts.dataFrame import transform_data
import pandas as pd

class TestBinanceData(unittest.TestCase):
    @patch('scripts.dataFrame.requests.get')
    def test_transform_data(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            [1629308400000, '42000.00', '42500.00', '41500.00', '42050.00', '100',
             1629312000000, '42000.00', 50, '50', '50', '0']
        ]
        df = transform_data()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 1)
        self.assertEqual(df['Open Time'][0], pd.to_datetime(1629308400000, unit='ms'))

if __name__ == '__main__':
    unittest.main()
