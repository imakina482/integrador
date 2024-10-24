import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_csv_to_parquet(input_file='/opt/integrador/datos/enriched_data.csv', output_file='/opt/integrador/datos/enriched_data.parquet'):
    """
    Convierte un archivo CSV a formato Parquet y lo guarda, asegurando que las columnas necesarias están presentes.

    Args:
        input_file (str): Ruta del archivo CSV de entrada.
        output_file (str): Ruta del archivo Parquet de salida.
    """
    try:
        df = pd.read_csv(input_file, names=['symbol', 'price', 'timestamp'], header=None)
        logging.info("Archivo CSV cargado exitosamente desde %s", input_file)     
        df['volume'] = 0.0 
        df['fecha_inicio'] = pd.to_datetime('now')
        df['fecha_fin'] = None
        df['registro_actual'] = True

       
        df = df[['timestamp', 'price', 'volume', 'symbol', 'fecha_inicio', 'fecha_fin', 'registro_actual']]

        # Convertir a formato Parquet
        df.to_parquet(output_file, index=False)
        logging.info("Archivo convertido y guardado en formato Parquet en %s", output_file)

    except FileNotFoundError:
        logging.error("El archivo %s no fue encontrado.", input_file)
    except Exception as e:
        logging.error("Ocurrió un error al convertir el archivo CSV a Parquet: %s", e)

if __name__ == "__main__":
    convert_csv_to_parquet()
