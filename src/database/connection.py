
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

base_dir = os.path.dirname(os.path.abspath(__file__))

csv_path = os.path.join(base_dir, '..', '..', 'data', 'all', 'all_products.csv')

products_df = pd.read_csv(csv_path)
products_df.drop("Unnamed: 0", inplace=True, axis=1)

products_dict =  products_df.to_dict(orient='records')

result = collection.insert_many(products_dict)


finish_time = time.time() - start_time

client.close()

print(type(result))
# print(f'Inserted {len(list(result))} products into MongoDB')
print(f'Finished in {finish_time:.5f} seconds')