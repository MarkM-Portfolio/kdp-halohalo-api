#! /var/www/html/kdp-halohalo-api/venv/bin/python3.6
from app import create_app
from os import environ
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from dotenv import load_dotenv

# Sentry here
load_dotenv()
SENTRY_DSN = environ.get("SENTRY_DSN")
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[FlaskIntegration()],
    environment = "development",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    max_breadcrumbs=50,
    debug=True,
)

application = create_app()

if __name__ == "__main__":
    application.run()


