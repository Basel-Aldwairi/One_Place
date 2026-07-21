from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
import pandas as pd
import time


class Database:

    def __init__(self):
        load_dotenv()

        start_time = time.time()

        self.uri = os.getenv("MONGO_URI")

        self.client = MongoClient(self.uri, server_api=ServerApi('1'))

        connectio_time = time.time() - start_time

        self.db = self.client[os.getenv("MONGO_DB")]
        self.collection = self.db[os.getenv("MONGO_COLLECTION")]

        print(f'Connected to MongoDB in {connectio_time:.5f} seconds')

    def delete_all(self):
        start_time = time.time()
        self.collection.remove({})
        finish_time = time.time() - start_time
        print(f'Deleted all products in {finish_time:.5f} seconds')

    def push_all(self):
        start_time = time.time()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, '..', '..', 'data', 'all', 'all_products.csv')

        products_df = pd.read_csv(csv_path)

        products_dict = products_df.to_dict(orient='records')
        self.collection.insert_many(products_dict)
        finish_time = time.time() - start_time

        print(f'Pushed all products in {finish_time:.5f} seconds')


    def pull_all(self) -> pd.DataFrame:
        start_time = time.time()

        products = self.collection.find({})
        products_df = pd.DataFrame.from_records(products)

        finish_time = time.time() - start_time
        print(f'Pull all products in {finish_time:.5f} seconds')

        return products_df