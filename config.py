from os import environ
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base config"""

    SEGP_DB = "segmentation_platform"
    SEGMENTS_COLLECTION = "segments"
    SEGMENTS_STATS_COLLECTION = "segments_stats"

    AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY")


class DevelopmentConfig(Config):
    ENVIRONMENT = "DEV"
    SEGP_MONGO_CLUSTER = "dev-segp-dedicated.q0znb.mongodb.net"


class TestingConfig(Config):
    ENVIRONMENT = "TEST"
    SEGP_DB = "test_segmentation_platform"
    SEGP_MONGO_CLUSTER = "dev-segp-cluster.q0znb.mongodb.net"


class ProductionConfig(Config):
    ENVIRONMENT = "PROD"
    SEGP_MONGO_CLUSTER = "live-segp.q0znb.mongodb.net"
