"""
Production settings - import from settings.py when ENV_TYPE=prod.
Override only what differs from base settings.
"""
import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .settings import *  # noqa: F401,F403

DEBUG = False

# Sentry error tracking
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

# AWS S3 Storage
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME", "")
AWS_S3_REGION_NAME = os.environ.get("AWS_SES_REGION_NAME", "eu-west-1")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_DEFAULT_ACL = "private"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# Email via SES
EMAIL_BACKEND = "django_ses.SESBackend"
AWS_SES_REGION_NAME = os.environ.get("AWS_SES_REGION_NAME", "eu-west-1")

# Logging for production
LOGGING["handlers"]["console"]["filters"] = []  # noqa: F405
LOGGING["handlers"]["console"]["level"] = "WARNING"  # noqa: F405
