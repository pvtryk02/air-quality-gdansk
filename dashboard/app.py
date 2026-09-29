import streamlit as st
import pandas as pd
import psycopg2

DB_HOST = "postgres"
DB_NAME = "airquality"
DB_USER = "airuser"
DB_PASSWORD = "airpassword"

STATIONS = [
    "PmGdaWyzwole",
    "PmGdaPowWars",
    "PmGdaGrunwal"
]

st.set_page_config(
    page_title="Air Quality Gdańsk",
    page_icon="🌫️",
    layout="wide"
)

st.title("🌫️ Air Quality Gdańsk")
st.write("Pomiary jakości powietrza oraz prognoza PM2.5 i PM10 na 24 godziny.")

station = st.selectbox(
    "Wybierz stację:",
    STATIONS
)

conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

measurements_query = """
SELECT measured_at, pm25, pm10
FROM measurements
WHERE station_code = %s
  AND pm25 IS NOT NULL
  AND pm10 IS NOT NULL
ORDER BY measured_at;
"""

forecast_query = """
SELECT forecast_at, pm25_forecast, pm10_forecast
FROM forecasts
WHERE station_code = %s
ORDER BY forecast_at;
"""

measurements = pd.read_sql_query(
    measurements_query,
    conn,
    params=(station,)
)

forecasts = pd.read_sql_query(
    forecast_query,
    conn,
    params=(station,)
)

conn.close()

measurements["measured_at"] = pd.to_datetime(
    measurements["measured_at"]
)

forecasts["forecast_at"] = pd.to_datetime(
    forecasts["forecast_at"]
)

# Ostatni pomiar
if not measurements.empty:
    latest = measurements.iloc[-1]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "PM2.5",
        f"{latest['pm25']:.1f} µg/m³"
    )

    col2.metric(
        "PM10",
        f"{latest['pm10']:.1f} µg/m³"
    )

    col3.metric(
        "Ostatni pomiar",
        latest["measured_at"].strftime("%d.%m.%Y %H:%M")
    )

st.subheader("Historia pomiarów")

history_chart = measurements.set_index("measured_at")[
    ["pm25", "pm10"]
]

history_chart = history_chart.rename(
    columns={
        "pm25": "PM2.5",
        "pm10": "PM10"
    }
)

st.line_chart(history_chart)

st.subheader("Prognoza na 24 godziny")

forecast_chart = forecasts.set_index("forecast_at")[
    ["pm25_forecast", "pm10_forecast"]
]

forecast_chart = forecast_chart.rename(
    columns={
        "pm25_forecast": "PM2.5 prognoza",
        "pm10_forecast": "PM10 prognoza"
    }
)

st.line_chart(forecast_chart)

st.subheader("Tabela prognozy")

forecast_table = forecasts.copy()

forecast_table["forecast_at"] = forecast_table[
    "forecast_at"
].dt.strftime("%d.%m.%Y %H:%M")

forecast_table = forecast_table.rename(
    columns={
        "forecast_at": "Data i godzina",
        "pm25_forecast": "PM2.5 [µg/m³]",
        "pm10_forecast": "PM10 [µg/m³]"
    }
)

forecast_table["PM2.5 [µg/m³]"] = forecast_table[
    "PM2.5 [µg/m³]"
].round(1)

forecast_table["PM10 [µg/m³]"] = forecast_table[
    "PM10 [µg/m³]"
].round(1)

st.dataframe(
    forecast_table,
    use_container_width=True,
    hide_index=True
)
