import json
import psycopg2
from confluent_kafka import Consumer

KAFKA_BROKER = "redpanda:9092"
KAFKA_TOPIC = "air-quality.raw"

DB_HOST = "postgres"
DB_NAME = "airquality"
DB_USER = "airuser"
DB_PASSWORD = "airpassword"

consumer = Consumer({
    "bootstrap.servers": KAFKA_BROKER,
    "group.id": "air-quality-consumer",
    "auto.offset.reset": "earliest"
})

consumer.subscribe([KAFKA_TOPIC])

conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

print("Consumer started...")

while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue

    if msg.error():
        print("Kafka error:", msg.error())
        continue

    try:
        data = json.loads(msg.value().decode("utf-8"))

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
        data.get("station_code"),
        data.get("measured_at"),
        data.get("pm25"),
        data.get("pm10"),
        data.get("temperature"),
        data.get("humidity"),
        data.get("pressure"),
        data.get("source")
    )
)

        conn.commit()

        print("Saved measurement:", data)

    except Exception as e:
        print("Processing error:", e)
        conn.rollback()