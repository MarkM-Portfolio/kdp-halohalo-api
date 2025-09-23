from kumuniverse.mongodb import Mongo


class MongoDB:
    def __init__(self):
        self.app = None
        self.segp_client = None

    def init_app(self, app):
        self.app = app
        self.create_segp_conn()

    def create_segp_conn(self):
        aws_access_key_id = self.app.config["AWS_ACCESS_KEY_ID"]
        aws_secret_access_key = self.app.config["AWS_SECRET_ACCESS_KEY"]
        mongo_cluster = self.app.config["SEGP_MONGO_CLUSTER"]
        self.segp_client = Mongo(
            aws_access_key_id, aws_secret_access_key, mongo_cluster
        )
        return self.segp_client

    def get_segp_client(self):
        if not self.segp_client:
            return self.create_segp_conn()
        return self.segp_client
