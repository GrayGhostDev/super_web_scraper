import sentry_sdk
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
import os

def init_sentry():
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        environment=os.getenv('ENVIRONMENT', 'development'),
        traces_sample_rate=1.0,
        integrations=[
            RedisIntegration(),
            SqlalchemyIntegration(),
            CeleryIntegration(),
        ],
        send_default_pii=False,
        max_breadcrumbs=50,
        debug=os.getenv('ENVIRONMENT') == 'development',
        attach_stacktrace=True,
        request_bodies='medium',
    )