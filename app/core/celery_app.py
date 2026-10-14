from celery import Celery
from celery.schedules import crontab

from app.core.config import settings


celery_app = Celery(
    "index_price",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    "collect-btc-price-every-minute": {
        "task": "index_price.collect",
        "schedule": crontab(),  # Каждую минуту
        "args": ("btc_usd",),
    },
    "collect-eth-price-every-minute": {
        "task": "index_price.collect",
        "schedule": crontab(),
        "args": ("eth_usd",),
    },
}