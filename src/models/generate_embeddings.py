import numpy as np
import pandas as pd
import os
from sentence_transformers import SentenceTransformer
import time

def generate_embeddings():

    start_time = time.time()

    print('Reading CSV...')
    df = pd.read_csv('../../data/all/all_products.csv')

    text_to_embed = df['model_text'].astype(str).tolist()

    print('Loading model...')
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, '..', 'models', 'embeddings_model')

    model = SentenceTransformer(model_path)


    print('Generating embeddings...')
    embeddings = model.encode(text_to_embed, show_progress_bar=True)

    print('Saving embeddings...')
    np.save('../../data/all/embeddings.npy', embeddings)

    end_time = time.time()

    generation_time = end_time - start_time

    print(f'Saved {embeddings.shape[0]} embeddings with {embeddings.shape[1]} dimensions')
    print(f'Finished in {generation_time:.2f} seconds')


if __name__ == '__main__':
    generate_embeddings()