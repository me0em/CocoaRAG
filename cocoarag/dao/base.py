from typing import Any
import os
import yaml
from box import Box

from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

import psycopg


class DAO:
    """ Basic DAO implementation
    """
    def __init__(self, config_path="../configs/credits.yml"):
        self.config = self._load_config(config_path)
        self.embeddings = OpenAIEmbeddings(
            model=self.config.embeddings_model.open_ai.embed_model,
            api_key=self.config.embeddings_model.open_ai.token
        )
        self.connection_string = self.config['database']['connection_string']
        self.connection_params = {
            "dbname": self.config['database']['dbname'],
            "user": self.config['database']['user'],
            "password": self.config['database']['password'],
            "host": self.config['database']['host'],
            "port": self.config['database']['port']
        }

    def _load_config(self, path) -> Box:
        """Load config and return it as a Box representation."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, path)
        config_path = os.path.normpath(config_path)
        try:
            with open(config_path, "r") as file:
                data: dict = yaml.safe_load(file)
            return Box(data)
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            raise

    def get_connection(self):
        try:
            conn = psycopg.connect(**self.connection_params)
            return conn
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def get_vector_store(self, collection_name: str):
        try:
            vector_store = PGVector(
                connection=self.connection_string,
                embeddings=self.embeddings,
                collection_name=collection_name,
                use_jsonb=True,
            )

            return vector_store
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def __call__(*args, **kwargs) -> Any: ...


if __name__ == "__main__":
    print(PGVector.__doc__)