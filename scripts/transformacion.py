# 1. Selecciono algunas columnas relevantes
df = df[['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume']]

df.columns = ['Timestamp', 'Open Price', 'High Price', 'Low Price', 'Close Price', 'Volume']

# Cambio a tipo float
df['Open Price'] = df['Open Price'].astype(float)
df['High Price'] = df['High Price'].astype(float)
df['Low Price'] = df['Low Price'].astype(float)
df['Close Price'] = df['Close Price'].astype(float)
df['Volume'] = df['Volume'].astype(float)

# Calculo diferencia entre el precio de cierre y apertura
df['Price Change'] = df['Close Price'] - df['Open Price']

# Obtengo solo datos de dìas con cambio de precio +
df_positive_change = df[df['Price Change'] > 0]

# Muestro resultados
print(df.head())
print("DataFrame con cambios positivos:")
print(df_positive_change.head())
