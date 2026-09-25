import psycopg2
from sentence_transformers import SentenceTransformer

DB_HOST = "postgres"
DB_NAME = "airquality"
DB_USER = "airuser"
DB_PASSWORD = "airpassword"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

documents = [
    {
        "content": "PmGdaWyzwole jest stacją pomiarową GIOŚ w Gdańsku. System zbiera z niej dane PM2.5 i PM10.",
        "source": "station"
    },
    {
        "content": "PmGdaPowWars jest stacją pomiarową GIOŚ w Gdańsku. System zbiera z niej dane PM2.5 i PM10.",
        "source": "station"
    },
    {
        "content": "PmGdaGrunwal jest stacją pomiarową GIOŚ w Gdańsku. System zbiera z niej dane PM2.5 i PM10.",
        "source": "station"
    },
    {
        "content": "System generuje prognozę PM2.5 i PM10 na kolejne 24 godziny dla każdej z trzech stacji.",
        "source": "forecast"
    },
    {
        "content": "Dane z API GIOŚ trafiają przez Node-RED do Redpanda, następnie consumer zapisuje je do PostgreSQL.",
        "source": "architecture"
    }
]

conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

cursor.execute("DELETE FROM knowledge_base;")

for doc in documents:
    embedding = model.encode(doc["content"]).tolist()

    cursor.execute(
        """
        INSERT INTO knowledge_base (
            content,
            source,
            embedding
        )
        VALUES (%s, %s, %s)
        """,
        (
            doc["content"],
            doc["source"],
            embedding
        )
    )

conn.commit()

question = "Jak działa prognozowanie jakości powietrza?"

question_embedding = model.encode(question).tolist()

cursor.execute(
    """
    SELECT
        content,
        source,
        embedding <=> %s::vector AS distance
    FROM knowledge_base
    ORDER BY embedding <=> %s::vector
    LIMIT 3;
    """,
    (
        question_embedding,
        question_embedding
    )
)

rows = cursor.fetchall()

print()
print("Question:")
print(question)

print()
print("Retrieved context:")

for content, source, distance in rows:
    print()
    print(f"[{source}] distance={distance:.4f}")
    print(content)

cursor.close()
conn.close()