import unittest
from scripts.dataFrame import transform_data
import pandas as pd

class TestBinanceData(unittest.TestCase):
    def test_transform_data(self):
        df = transform_data()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertEqual(len(df.columns), 12) 
        self.assertIn('Open Time', df.columns)

if __name__ == '__main__':
    unittest.main()

