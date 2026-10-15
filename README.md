# Сбор индексных цен Deribit

Приложение раз в минуту получает индексные цены `btc_usd` и `eth_usd` через
`public/get_index_price` Deribit, сохраняет их в PostgreSQL и предоставляет
GET API на FastAPI для чтения истории. Планировщик Celery Beat ставит задание
в очередь Redis, Celery worker выполняет запросы и запись в базу.

## Запуск через Docker Compose

Нужны Docker и Docker Compose. Из корня проекта выполните:

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f app celery celery-beat
```

PostgreSQL и Redis проверяются через healthcheck. Контейнер `app` запускает
миграции Alembic и API после готовности PostgreSQL; worker и beat запускаются
после готовности API и Redis. API доступно по адресу
`http://localhost:8000/docs`. Первая запись появится после ближайшего запуска
задания в начале минуты. Данные PostgreSQL и Redis хранятся в Docker volumes.

По умолчанию в Compose используются база, пользователь и пароль `app`.
Их можно изменить переменными `POSTGRES_DB`, `POSTGRES_USER` и
`POSTGRES_PASSWORD` до запуска. Для остановки контейнеров:

```bash
docker compose down
```

Эта команда сохраняет volumes с данными.

## API

Все методы используют обязательный query-параметр `ticker`. Допустимые значения:
`btc_usd` и `eth_usd`. В ответе запись содержит `id`, `ticker`, `price` и
`timestamp` (UNIX-секунды, UTC).

| Метод | Назначение | Дополнительные параметры |
| --- | --- | --- |
| `GET /api/v1/index-prices` | Все записи валюты, от новых к старым | `limit` (1–1000, необязательный), `offset` (от 0) |
| `GET /api/v1/index-prices/last` | Последняя сохранённая цена | Нет |
| `GET /api/v1/index-prices/by-timestamp` | Цена за минуту, в которую попадает указанное время | `timestamp` — обязательный UNIX timestamp в секундах |

Примеры запросов:

```bash
curl 'http://localhost:8000/api/v1/index-prices?ticker=btc_usd'
curl 'http://localhost:8000/api/v1/index-prices/last?ticker=eth_usd'
curl 'http://localhost:8000/api/v1/index-prices/by-timestamp?ticker=btc_usd&timestamp=1760486475'
```

Для `by-timestamp` можно передать любую секунду нужной минуты: время
округляется вниз до её начала. Если запись не найдена, методы `last` и
`by-timestamp` возвращают JSON `null`; список возвращает `[]`. Некорректные
параметры возвращают HTTP 422.

Интерактивная документация: [Swagger UI](http://localhost:8000/docs),
[ReDoc](http://localhost:8000/redoc),
[OpenAPI JSON](http://localhost:8000/openapi.json).

## Запуск без Compose

Нужны Python 3.12+, Poetry, запущенные PostgreSQL и Redis. Установите
зависимости командой `poetry install --no-root`, затем задайте переменные
окружения (можно сохранить их в `.env` в корне проекта):

```dotenv
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/app
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

Создайте базу и примените миграции. Для миграций и API достаточно
`DATABASE_URL`; для worker и beat дополнительно нужны обе переменные Celery.
В отдельных терминалах запустите:

```bash
poetry run alembic upgrade head
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
poetry run celery -A app.core.celery_app:celery_app worker --loglevel=INFO
poetry run celery -A app.core.celery_app:celery_app beat --loglevel=INFO
```

При изменении модели создайте ревизию командой
`poetry run alembic revision --autogenerate -m "описание"`, проверьте
сгенерированный файл и примените её через `poetry run alembic upgrade head`.

## Тесты

Тесты написаны на `pytest` и `pytest-asyncio`. После установки dev-зависимостей
их можно запустить командой:

```bash
poetry install --with dev --no-root
poetry run pytest
```

Тесты используют mock-объекты; для их запуска не нужны работающие PostgreSQL,
Redis и доступ к Deribit.

## Проектные решения (Design decisions)

### Время и уникальность данных

Время сбора хранится как UNIX timestamp в секундах UTC и округляется до
начала минуты. Уникальное ограничение PostgreSQL на `(ticker, timestamp)`
исключает повторную запись за ту же минуту. При повторной попытке сохраняется
время исходного задания, поэтому задержка Celery не переносит запись в
следующую минуту. Повторный сбор за минуту оставляет первую сохранённую цену.

### Получение и сохранение цен

Deribit возвращает индексные цены по одному тикеру. Два HTTP-запроса выполняются
параллельно через `aiohttp`, а цены сохраняются одной транзакцией: если один
запрос или запись не удались, частичной пары в базе не остаётся. Значение
разбирается как `Decimal` и хранится в PostgreSQL `NUMERIC(24, 8)`, чтобы
избежать погрешностей двоичного `float`.

### Celery и обработка ошибок

Celery Beat планирует сбор каждую минуту, Redis служит брокером задач. Внешний
HTTP, ответ Deribit и операции SQLAlchemy могут завершиться временной ошибкой;
для них настроены до трёх повторов с увеличением задержки. Worker запускает
асинхронный код через `asyncio.run`, так как задача Celery синхронная.

### Структура и развёртывание

API, сервис, репозиторий, Deribit-клиент и задача Celery разделены по
ответственности. Dishka предоставляет сервисам сессию БД в рамках запроса.
Настройки БД и Celery разделены: миграции и API не требуют конфигурации
брокера. Alembic управляет схемой базы; контейнер API применяет миграции до
запуска сервера, а healthcheck-зависимости Compose задают порядок запуска
остальных сервисов.
