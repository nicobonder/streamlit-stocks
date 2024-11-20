import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# Pedir al usuario los tickers desde la terminal
print("Enter the ticker symbols you want to work with (e.g., MSFT, AAPL, GOOG):")
ticker_graph = input(
    "Enter the ticker for the price evolution graph: ").strip().upper()
ticker1 = input(
    "Enter the first ticker for correlation analysis: ").strip().upper()
ticker2 = input(
    "Enter the second ticker for correlation analysis: ").strip().upper()


# Descargar datos para los tickers seleccionados
tickers = [ticker_graph, ticker1, ticker2]
tickersInfo = yf.download(tickers, start='2021-04-30')


# Seleccionar la columna 'Adj Close'
df_adj_close = tickersInfo['Adj Close']

# Resetear el índice para convertir el índice datetime en una columna
df_adj_close = df_adj_close.reset_index()

# Renombrar la columna de fecha para mayor claridad
# df_adj_close.rename(columns={'Date': 'date'}, inplace=True)

# Asegurarse de que la columna de fechas esté en formato datetime (parsear)
df_adj_close['Date'] = df_adj_close['Date'].dt.date

# Mostrar el DataFrame resultante
print(df_adj_close)

# Gráfico para el ticker seleccionado
if ticker_graph in df_adj_close.columns:
    fig_graph = go.Figure()
    fig_graph.add_trace(go.Scatter(
        x=df_adj_close['Date'], y=df_adj_close[ticker_graph], mode='lines', name=ticker_graph))
    fig_graph.update_layout(title=f"Price Evolution of {ticker_graph}",
                            xaxis_title='Date', yaxis_title='Price')
    fig_graph.show()
else:
    print(f"Ticker '{ticker_graph}' not found in the data.")


# Calcular correlacion entre 2 tickers
# Calculamos los cambios porcentuales para cada ticker
df_changes = df_adj_close.set_index('Date').pct_change()

# Elegimos dos tickers
if ticker1 in df_changes.columns and ticker2 in df_changes.columns:
    df_correlation = df_changes[[ticker1, ticker2]].dropna()

    # Extraemos las columnas de los dos tickers seleccionados
    df_correlation = df_changes[[ticker1, ticker2]].dropna()

    # Calculamos la correlación entre los dos tickers
    correlation = df_correlation[ticker1].corr(df_correlation[ticker2])
    print(f"The correlation between {ticker1} and {
          ticker2} is: {correlation:.2f}")

    # Crear el gráfico de dispersión para mostrar la relación
    fig_corr = px.scatter(
        df_correlation,
        x=ticker1,
        y=ticker2,
        title=f"Correlation Between {ticker1} and {
            ticker2}: {correlation:.2f}",
        labels={ticker1: f"Percentage Change in {ticker1}",
                ticker2: f"Percentage Change in {ticker2}"},
        trendline="ols"  # Ajusta una línea de tendencia
    )
    fig_corr.show()
else:
    print(f"One or both tickers ('{ticker1}', '{
          ticker2}') not found in the data.")

# Gráfico con todos los tickers
# fig_all = go.Figure()
# # Desde la segunda columna para omitir 'date'
# for ticker in df_adj_close.columns[1:]:
#     fig_all.add_trace(go.Scatter(
#         x=df_adj_close['date'], y=df_adj_close[ticker], mode='lines', name=ticker))

# fig_all.update_layout(title='Price Evolution of All Tickers',
#                       xaxis_title='Date', yaxis_title='Price')
# fig_all.show()


# Gráfico para un ticker específico (e.g., AAPL)
# fig_aapl = go.Figure()
# fig_aapl.add_trace(go.Scatter(
#     x=df_adj_close['date'], y=df_adj_close['AAPL'], mode='lines', name='AAPL'))
# fig_aapl.update_layout(title='Price Evolution of AAPL',
#                        xaxis_title='Date', yaxis_title='Price')
# fig_aapl.show()
