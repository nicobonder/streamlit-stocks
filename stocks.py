import matplotlib.pyplot as plt
import pandas_datareader as pdr
import streamlit as st
import yfinance as yfin
import seaborn as sns
import datetime
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')


# yfin.pdr_override()

warnings.filterwarnings('ignore')


# Tickers to consider in our analisis:
tickers = ["GOOGL", "RCL", "UAL", "NVDA"]
start = "2021-4-1"
end = "2024-11-1"

df_stocks = yfin.download(tickers, start=start,
                          end=end, group_by='ticker')

# print(df_stocks.shape)

# pd.options.display.max_columns = None
# df_stocks.head()


# Buscar info de los precios de cierre ajustados
# Acceder a la columna 'Adj Close' de cada ticker
df_stocks_adj_close = df_stocks.xs('Adj Close', level=1, axis=1)


# Extraer las columnas 'Open' y 'Volume' y mantener el ticker como índice en las columnas
df_open_vol = df_stocks.loc[:, (slice(None), ['Open', 'Volume'])]

# Concatenar los niveles de columnas para tener columnas con nombres únicos
df_open_vol.columns = [f"{ticker}_{
    col}" for ticker, col in df_open_vol.columns]

# Crear un nuevo dtaframe
df_marketCap = pd.DataFrame()

for ticker in tickers:
    df_marketCap[f'{ticker}_MKTCap'] = df_open_vol[f'{
        ticker}_Open'] * df_open_vol[f'{ticker}_Volume']

# Crear los gráficos
plt.rcParams['figure.figsize'] = (10, 4)
df_marketCap['GOOGL_MKTCap'].plot(label='Google')
df_marketCap['NVDA_MKTCap'].plot(label='Nvidia')
df_marketCap['RCL_MKTCap'].plot(label='RCL')
df_marketCap['UAL_MKTCap'].plot(label='UAL')

# Agregar título y leyenda
plt.title("Market Cap")
plt.legend()  # Leyenda para las series de datos
plt.xticks(rotation=45)  # Rotar las etiquetas del eje X
plt.tight_layout()  # Ajuste de los márgenes para que no se corten las etiquetas

# Mostrar el gráfico en Streamlit
st.pyplot(plt)

# Calculamos el cambio diario
# Para eso primero creamos una nueva columna
df_google_adj_close = df_stocks_adj_close['day_perc_change'] = df_stocks_adj_close['GOOGL'].pct_change(
)*100

# Remove missing data
df_google_adj_close.dropna(axis=0, inplace=True)

# Dibujamos el grafico
plt.rcParams['figure.figsize'] = (10, 4)
df_google_adj_close['day_perc_change'].plot(label='Google %')


plt.title('google cambio diario en %')
plt.legend()  # Leyenda para las series de datos
plt.xticks(rotation=45)  # Rotar las etiquetas del eje X
plt.tight_layout()
