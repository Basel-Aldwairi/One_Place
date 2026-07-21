
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
import pandas as pd
import time


load_dotenv()

start_time = time.time()


uri = os.getenv("MONGO_URI")

client = MongoClient(uri, server_api=ServerApi('1'))

connectio_time = time.time() - start_time

print(f'Connected to MongoDB in {connectio_time:.5f} seconds')

db = client[os.getenv("MONGO_DB")]
collection = db[os.getenv("MONGO_COLLECTION")]

collection.delete_many({})

finish_time = time.time() - start_time

print(f'Finished in {finish_time:.5f} seconds')