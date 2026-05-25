import os
from sentence_transformers import SentenceTransformer

os.makedirs("../models/embeddings_model", exist_ok=True)

print('downloading all-MiniLM-L6-v2...')
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model loaded')

model.save('../models/embeddings_model')
print('Model successfully downloaded')