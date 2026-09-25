# Air Quality Gdańsk — szybkie uruchomienie

## Wymagania

- Docker Desktop
- Docker Compose

## Start projektu

W katalogu projektu uruchom:

```bash
docker compose up -d
```

Opcjonalnie możesz sprawdzić status kontenerów:

```bash
docker compose ps
```

## Adresy aplikacji

Dashboard:

```text
http://localhost:8501
```

Node-RED:

```text
http://localhost:1880
```

Redpanda Console:

```text
http://localhost:8080
```

PostgreSQL:

```text
localhost:5432
```

Kafka / Redpanda:

```text
localhost:19092
```

## RAG / pgvector

Jednorazowe uruchomienie modułu RAG:

```bash
docker compose run --rm rag
```

## Zatrzymanie projektu

```bash
docker compose down
```

## Główny przepływ danych

```text
GIOŚ API
→ Node-RED
→ Redpanda / Kafka
→ Python Consumer
→ PostgreSQL + pgvector
→ Forecasting
→ Dashboard
```
