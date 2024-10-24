import pandas as pd
import logging
from transformacion import calculate_price_difference

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Columnas requeridas para el procesamiento
REQUIRED_COLUMNS = ['Open Price', 'Close Price']

def process_binance_data(input_file='/opt/integrador/datos/binance_prices.csv', output_file='/opt/integrador/datos/enriched_data.csv'):
    """
    Procesa los datos de precios de Binance y calcula la diferencia de precios.

    Args:
        input_file (str): Ruta del archivo CSV de entrada.
        output_file (str): Ruta del archivo CSV de salida.
    """
    try:
        # Verificar la existencia del archivo de entrada
        if not pd.io.common.file_exists(input_file):
            logging.error("El archivo %s no fue encontrado.", input_file)
            return

        # Cargar datos
        df = pd.read_csv(input_file)
        logging.info("Datos cargados exitosamente desde %s", input_file)

        # Verificar que las columnas requeridas están en el DataFrame
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            logging.error("Las siguientes columnas están ausentes en el archivo: %s", missing_columns)
            return

        # Calcular la diferencia de precios
        df['price_difference'] = df.apply(
            lambda row: calculate_price_difference(row['Open Price'], row['Close Price']),
            axis=1
        )

        # Manejo valores NaN si existen
        df.fillna(0, inplace=True)

        # Guardo los datos enriquecidos
        df.to_csv(output_file, index=False)
        logging.info("Datos enriquecidos guardados en %s", output_file)

    except pd.errors.EmptyDataError:
        logging.error("El archivo %s está vacío.", input_file)
    except pd.errors.ParserError:
        logging.error("El archivo %s no es un CSV válido.", input_file)
    except Exception as e:
        logging.error("Ocurrió un error al procesar los datos: %s", e)

if __name__ == "__main__":
    process_binance_data()
