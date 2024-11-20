import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import datetime
import pandas as pd

# Título
st.title("Stock Price and Correlation Analysis")

# Panel de Inputs
st.sidebar.header("Choose your tickers")

# Obtener los tickers seleccionados
ticker_graph = st.sidebar.text_input(
    "Enter the ticker for the price evolution graph:", "AAPL").strip().upper()
ticker1 = st.sidebar.text_input(
    "Enter the first ticker for correlation analysis:", "AAPL").strip().upper()
ticker2 = st.sidebar.text_input(
    "Enter the second ticker for correlation analysis:", "GOOG").strip().upper()

today = datetime.date.today()

# Choose start date
startDate = st.sidebar.date_input("Start date: ", datetime.date(2021, 7, 6))

# Choose end date
endDate = st.sidebar.date_input("End date: ", today)  # Por defecto, hoy

# Ajustar la fecha de finalización si es menor que hoy
if endDate <= today:
    endDate_adjusted = endDate + datetime.timedelta(days=1)
else:
    endDate_adjusted = endDate


# Botón para actualizar los gráficos
if st.sidebar.button("Submit"):
    # Descargar datos para los tickers seleccionados
    tickers = [ticker_graph, ticker1, ticker2]
    tickersInfo = yf.download(tickers, start=startDate, end=endDate_adjusted)

    # Seleccionar la columna 'Adj Close'
    df_adj_close = tickersInfo['Adj Close']

    # Resetear el índice para convertir el índice datetime en una columna
    df_adj_close = df_adj_close.reset_index()

    # Asegurarse de que la columna de fechas esté en formato datetime (parsear)
    df_adj_close['Date'] = df_adj_close['Date'].dt.date

    # Mostrar el DataFrame en Streamlit
    st.write(df_adj_close)

    # Gráfico para el ticker seleccionado
    if ticker_graph in df_adj_close.columns:
        fig_graph = go.Figure()
        fig_graph.add_trace(go.Scatter(
            x=df_adj_close['Date'], y=df_adj_close[ticker_graph], mode='lines', name=ticker_graph))
        fig_graph.update_layout(title=f"Price Evolution of {ticker_graph}",
                                xaxis_title='Date', yaxis_title='Price')
        st.plotly_chart(fig_graph)
    else:
        st.warning(f"Ticker '{ticker_graph}' not found in the data.")

    # Calcular correlación entre 2 tickers
    df_changes = df_adj_close.set_index('Date').pct_change()

    if ticker1 in df_changes.columns and ticker2 in df_changes.columns:
        df_correlation = df_changes[[ticker1, ticker2]].dropna()

        # Calculamos la correlación entre los dos tickers
        correlation = df_correlation[ticker1].corr(df_correlation[ticker2])
        st.subheader("Correlation graph")

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
        st.plotly_chart(fig_corr)
    else:
        st.warning(f"One or both tickers ('{ticker1}', '{
                   ticker2}') not found in the data.")
