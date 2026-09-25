import psycopg2
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

DB_HOST = "postgres"
DB_NAME = "airquality"
DB_USER = "airuser"
DB_PASSWORD = "airpassword"

STATIONS = [
    "PmGdaWyzwole",
    "PmGdaPowWars",
    "PmGdaGrunwal"
]

query = """
SELECT measured_at, pm25, pm10
FROM measurements
WHERE station_code = %s
  AND pm25 IS NOT NULL
  AND pm10 IS NOT NULL
ORDER BY measured_at;
"""

conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

for station in STATIONS:
    print()
    print("=" * 60)
    print(f"Forecasting station: {station}")
    print("=" * 60)

    df = pd.read_sql_query(
        query,
        conn,
        params=(station,)
    )

    df["measured_at"] = pd.to_datetime(df["measured_at"])
    df = df.set_index("measured_at")

    # Usuń ewentualne duplikaty czasu
    df = df[~df.index.duplicated(keep="last")]

    # Wymuś regularny odstęp co 1 godzinę
    df = df.asfreq("h")

    # Uzupełnij brakujące godziny interpolacją
    df["pm25"] = df["pm25"].interpolate(method="linear")
    df["pm10"] = df["pm10"].interpolate(method="linear")

    print("Loaded rows:", len(df))
    print()
    print(df.tail())

    if len(df) < 24:
        print(f"Skipping {station} - za mało danych.")
        continue

    # PM2.5
    model_pm25 = ExponentialSmoothing(
        df["pm25"],
        trend="add",
        seasonal=None
    ).fit()

    forecast_pm25 = model_pm25.forecast(24)

    # PM10
    model_pm10 = ExponentialSmoothing(
        df["pm10"],
        trend="add",
        seasonal=None
    ).fit()

    forecast_pm10 = model_pm10.forecast(24)

    last_time = df.index.max()

    future_dates = pd.date_range(
        start=last_time + pd.Timedelta(hours=1),
        periods=24,
        freq="h"
    )

    forecast = pd.DataFrame({
        "forecast_at": future_dates,
        "pm25_forecast": forecast_pm25.values,
        "pm10_forecast": forecast_pm10.values
    })

    print()
    print(f"24h forecast for {station}:")
    print()
    print(forecast.to_string(index=False))

    # Usuń poprzednią prognozę dla tej stacji
    cursor.execute(
        """
        DELETE FROM forecasts
        WHERE station_code = %s;
        """,
        (station,)
    )

    # Zapisz aktualną prognozę 24h
    for _, row in forecast.iterrows():
        cursor.execute(
            """
            INSERT INTO forecasts (
                station_code,
                forecast_at,
                pm25_forecast,
                pm10_forecast
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (station_code, forecast_at)
            DO UPDATE SET
                pm25_forecast = EXCLUDED.pm25_forecast,
                pm10_forecast = EXCLUDED.pm10_forecast,
                created_at = NOW()
            """,
            (
                station,
                row["forecast_at"],
                float(row["pm25_forecast"]),
                float(row["pm10_forecast"])
            )
        )

    conn.commit()

    print()
    print(f"Forecast saved for {station}.")

cursor.close()
conn.close()

print()
print("All forecasts finished.")