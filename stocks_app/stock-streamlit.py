import datetime
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd

# Título
st.title("Stock Price and Correlation Analysis")

# Panel de Inputs
st.sidebar.header("Choose your tickers")

# Obtener los tickers seleccionados
ticker_graph = st.sidebar.text_input(
    "Enter the ticker for the price evolution graph:", "APP").strip().upper()
ticker1 = st.sidebar.text_input(
    "Enter the first ticker for correlation analysis:", "APP").strip().upper()
ticker2 = st.sidebar.text_input(
    "Enter the second ticker for correlation analysis:", "GOOG").strip().upper()

today = datetime.date.today()

# Choose start date
startDate = st.sidebar.date_input("Start date: ", datetime.date(2023, 1, 1))

# Choose end date
endDate = st.sidebar.date_input("End date: ", today)  # Por defecto, hoy

# Ajustar la fecha de finalización si es menor que hoy
if endDate <= today:
    endDate_adjusted = endDate + datetime.timedelta(days=1)
else:
    endDate_adjusted = endDate

# Función para obtener los indicadores relevantes de un ticker


def get_ticker_data(ticker):
    dat = yf.Ticker(ticker)
    return {
        "Trailing P/E": dat.info.get("trailingPE"),
        "Forward P/E": dat.info.get("forwardPE"),
        "Trailing PEG Ratio": dat.info.get("trailingPegRatio"),
        "Price to Sales (TTM)": dat.info.get("priceToSalesTrailing12Months"),
        "Price to Book": dat.info.get("priceToBook"),
        "Operating Margins": dat.info.get("operatingMargins"),
        "Return on Assets": dat.info.get("returnOnAssets"),
        "Earnings Quarterly Growth": dat.info.get("earningsQuarterlyGrowth"),
        "Revenue Growth": dat.info.get("revenueGrowth"),
        "Debt to Equity": dat.info.get("debtToEquity"),
        "Current Ratio": dat.info.get("currentRatio"),
        "Beta": dat.info.get("beta"),
        "Held by Insiders": dat.info.get("heldPercentInsiders"),
        "Held by Institutions": dat.info.get("heldPercentInstitutions"),
        "Short Ratio": dat.info.get("shortRatio"),
        "Short % of Float": dat.info.get("shortPercentOfFloat"),
    }


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
    df_adj_close['Date'] = pd.to_datetime(df_adj_close['Date'])

    # DEspues agregar esta linea para convertir de nuevo a formato YY-MM-DD
    # df_adj_close['Date'] = df_adj_close['Date'].dt.date

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

        df_adj_close['Pct_Change'] = df_adj_close[ticker_graph].pct_change() * \
            100
        # Asegúrate de eliminar filas NaN creadas por `pct_change()`
        df_adj_close = df_adj_close.dropna(subset=['Pct_Change'])

        # Agregar el día de la semana
        df_adj_close['Day_of_Week'] = pd.Categorical(
            pd.to_datetime(df_adj_close['Date']).dt.day_name(),
            categories=['Monday', 'Tuesday',
                        'Wednesday', 'Thursday', 'Friday'],
            ordered=True
        )

    # Calcular el promedio de variación porcentual para cada día de la semana
    avg_pct_change = df_adj_close.groupby('Day_of_Week')['Pct_Change'].mean()

    # Resetear el índice para convertir los días de la semana en una columna
    avg_pct_change = avg_pct_change.reset_index()

    # Crear una columna auxiliar para asignar "Positive" o "Negative" en lugar de los colores
    avg_pct_change['Change Type'] = avg_pct_change['Pct_Change'].apply(
        lambda x: 'Positive' if x > 0 else 'Negative'
    )

    # Crear el histograma con "Positive" y "Negative" como etiquetas de color
    fig_histogram = px.bar(
        avg_pct_change,
        x='Day_of_Week',
        y='Pct_Change',
        title=f"Average Percentage Change by Day of the Week for {
            ticker_graph}",
        labels={'Pct_Change': 'Average % Change',
                'Day_of_Week': 'Day of the Week', 'Change Type': ''},
        color='Change Type',  # Usar la columna de cambio positivo/negativo
        color_discrete_map={'Positive': 'green',
                            'Negative': 'red'}  # Mapear colores
    )

    fig_histogram.update_layout(showlegend=False)
    # Mostrar el histograma en Streamlit
    st.plotly_chart(fig_histogram)

    # Feature: Calcular correlación entre 2 tickers
    df_changes = df_adj_close.select_dtypes(
        include=['float64', 'int']).set_index(df_adj_close['Date']).pct_change()

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

    # Crear un DataFrame para mostrar en la tabla
    # Obtener datos de los tickers
    st.subheader("Ticker Comparison")
    data1 = get_ticker_data(ticker1)
    data2 = get_ticker_data(ticker2)

    comparison_data = pd.DataFrame({
        "Indicator": data1.keys(),
        ticker1: data1.values(),
        ticker2: data2.values(),
    })

    # Mostrar tabla
    st.table(comparison_data)

    # Feature Heatmap
    # Extrae el mes y el día para crear una columna `Month-Day`
    df_adj_close['Month-Day'] = df_adj_close['Date'].dt.strftime('%m-%d')

    # Extrae el mes y el día para crear una columna `Month-Day`
    df_adj_close['Month'] = df_adj_close['Date'].dt.month
    df_adj_close['Day'] = df_adj_close['Date'].dt.day

    # Agrupa por `Month` y `Day` y calcula el promedio de `Pct_Change`
    avg_pct_change_by_day = df_adj_close.groupby(
        ['Month', 'Day'])['Pct_Change'].mean().reset_index()

    # Usa pivot_table para manejar posibles duplicados
    heatmap_data = avg_pct_change_by_day.pivot_table(
        index='Month',
        columns='Day',
        values='Pct_Change',
        fill_value=0
    )

    st.subheader(f"Average Daily % Change Heatmap - {ticker_graph}")
    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='RdYlGn',
            zmid=0,
            colorbar=dict(
                title="% Change",
                len=0.7,  # Control the colorbar height
            ),
            xgap=2,  # add gap between columns
            ygap=2  # add gap between rows
        )
    )

    # Ajusta el diseño del heatmap
    fig_heatmap.update_layout(
        xaxis_title="Day of Month",
        yaxis_title="Month",
        height=450,
        width=1400,
        margin=dict(l=0, r=0, t=0, b=0),
    )

    # Ajusta el tamaño de las celdas del heatmap
    fig_heatmap.update_xaxes(
        tickmode='array',
        tickvals=list(range(1, 32)),
        ticktext=[str(day) for day in range(1, 32)]
    )
    fig_heatmap.update_yaxes(
        tickmode='array',
        tickvals=list(range(1, 13)),
        ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        # scaleanchor="x",  # Vincula la escala de x y y
    )

    fig_heatmap.update_xaxes(fixedrange=True)  # Block the resize feature
    fig_heatmap.update_yaxes(fixedrange=True)  # Block the resize feature

    # Mostrar el heatmap en Streamlit
    st.plotly_chart(fig_heatmap)


else:
    st.warning(f"Ticker '{ticker_graph}' not found in the data.")


# *** IDEAS:
# 1. Correlacion entre crecimiento del precio de accion y alguna otra vble, tipo el crecimiento del EPS o de los revenue de los 3 trimestres anteriores.
# 2. Grafico de barras mostrando promedio de % de cambio para cada mes, asi se puede saber qué mes tiene más crecimiento o caida
# 3. Correlacion entre dia del mes y % de variacion. O sea grafico de 2 vbles mostrando los 31 dias del mes y el % de cambio promedio que tiene cada dia
# 4. plost.donut_chart mostrando % de veces que algo fue bull, bear o vario poco, por ejemplo.
    # Esto podria estar en una fila con 2 columnas, eso en una columna y en la otra lo mismo en una tabla.
# 5. Crear algun tipo de indicador como el de Zacks: elegir 3 o 4 medidas de crecimiento, ponderarlas y que el promedio de un puntaje, si está entre tal numero y tal numero, tiene una A, por ej.
# 6. Seleccion multiple: tomar de yahoo vbles como Trailing P/E, Forward P/E, PEG, Price/Sales, Operating Margin,  Return on Assets, Quarterly Revenue Growth, Quarterly Earnings Growth,
    # Total Debt/Equity, Current Ratio, Short Ratio, Short % of Float, Beta, % Held by Insiders, % Held by Institutions, Diluted EPS. Y que se pueda comparar 2 empresas con cualquiera de esas vbles.
    # Cada variable elegida por el user sería una nueva row y la tabla tendria 3 columnas: Variables, Ticker 1 y Ticker 2

    # Haciendo .info veo: trailingPE, forwardPE, trailingPegRatio, priceToSalesTrailing12Months, priceToBook, operatingMargins, returnOnAssets, earningsQuarterlyGrowth, revenueGrowth, debtToEquity, currentRatio, beta, heldPercentInsiders, heldPercentInstitutions, shortRatio, shortPercentOfFloat


# *** Mejoras pendientes:
# Data solo YY-MM-DD
