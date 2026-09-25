import requests
import psycopg2

DB_HOST = "postgres"
DB_NAME = "airquality"
DB_USER = "airuser"
DB_PASSWORD = "airpassword"

BASE_URL = "https://api.gios.gov.pl/pjp-api/v1/rest/data/getData"

STATIONS = [
    {
        "station_code": "PmGdaWyzwole",
        "pm10_id": 4706,
        "pm25_id": 27667
    },
    {
        "station_code": "PmGdaPowWars",
        "pm10_id": 4681,
        "pm25_id": 28227
    },
    {
        "station_code": "PmGdaGrunwal",
        "pm10_id": 26171,
        "pm25_id": 26172
    }
]


def fetch_all(sensor_id):
    page = 0
    result = []

    while True:
        url = f"{BASE_URL}/{sensor_id}?page={page}&size=20"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()
        values = data.get("Lista danych pomiarowych", [])
        result.extend(values)

        total_pages = data.get("totalPages", 1)

        if page >= total_pages - 1:
            break

        page += 1

    return result


conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

for station in STATIONS:
    print(f"Importing {station['station_code']}...")

    pm10_data = fetch_all(station["pm10_id"])
    pm25_data = fetch_all(station["pm25_id"])

    pm10_map = {
        x["Data"]: x["Wartość"]
        for x in pm10_data
        if x["Wartość"] is not None
    }

    pm25_map = {
        x["Data"]: x["Wartość"]
        for x in pm25_data
        if x["Wartość"] is not None
    }

    common_dates = sorted(set(pm10_map) & set(pm25_map))

    inserted = 0

    for measured_at in common_dates:
        cursor.execute(
            """
            INSERT INTO measurements (
                station_code,
                measured_at,
                pm25,
                pm10,
                temperature,
                humidity,
                pressure,
                source
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (station_code, measured_at) DO NOTHING
            """,
            (
                station["station_code"],
                measured_at,
                pm25_map[measured_at],
                pm10_map[measured_at],
                None,
                None,
                None,
                "GIOS_HISTORY"
            )
        )

        inserted += cursor.rowcount

    conn.commit()

    print(f"{station['station_code']} -> inserted rows: {inserted}")

cursor.close()
conn.close()

print("History import finished.")