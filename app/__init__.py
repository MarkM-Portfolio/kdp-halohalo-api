"""
This contains the application factory for creating flask application instances.
Using the application factory allows for the creation of flask applications configured
for different environments based on the value of the CONFIG_TYPE environment variable
"""

from os import environ
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from app.extensions import mongo

load_dotenv()


def create_app(env=None):
    app = Flask(__name__)
    CORS(app)

    # Configure app instance
    if env is None:
        env = environ.get("ENV")

    if env == "TEST":
        app.config.from_object("config.TestingConfig")
        print("Using Test Environment")
    elif env == "PROD":
        app.config.from_object("config.ProductionConfig")
        print("Using Production Environment")
    else:
        app.config.from_object("config.DevelopmentConfig")
        print("Using Development Environment")

    # Initialize extensions
    mongo.init_app(app)

    # Register blueprints
    register_blueprints(app)

    

    @app.route('/debug-sentry')
    def trigger_error():
        division_by_zero = 1 / 0

    # Health check
    @app.route("/halohalo/health")
    def yamashita():
        return "Welcome! You have successfully connected to HALOHALO Data Services"

    return app


def register_blueprints(app):
    from app.segments import segments_api

    app.register_blueprint(segments_api, url_prefix="/v1/segments")
