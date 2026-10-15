# Index Prices

Celery Beat schedules a price collection every minute. The worker fetches BTC and
ETH index prices from Deribit and saves both in one PostgreSQL transaction. The
FastAPI endpoints read the stored prices. Each ticker has at most one saved price
per UTC minute; a repeated collection in the same minute keeps the first value.

## Run with Docker Compose

```bash
docker compose up --build -d
docker compose logs migrate celery celery-beat
```

Compose waits for PostgreSQL, applies the Alembic migration, and then starts the
API and Celery services. The API is available at `http://localhost:8000/docs`.
Docker Desktop's WSL integration must be enabled when running these commands
inside WSL.
After the first collection, check a stored value:

```bash
curl 'http://localhost:8000/api/v1/index-prices/last?ticker=btc_usd'
```

## Migrations

`DATABASE_URL`, `CELERY_BROKER_URL`, and `CELERY_RESULT_BACKEND` are required
when running outside Compose. Apply migrations before starting the API or worker:

```bash
poetry run alembic upgrade head
```

For a model change, create a revision against a running database with
`poetry run alembic revision --autogenerate -m "describe change"`, review the
generated script, and apply it with `poetry run alembic upgrade head`.
