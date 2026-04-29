import numpy as np
import pandas as pd
from jedi.inference import names
from sentence_transformers import SentenceTransformer

def generate_embeddings():

    print('Reading CSV...')
    df = pd.read_csv('../../data/all/all_products.csv')

    text_to_embed = df['model_text'].astype(str).tolist()

    print('Loading model...')
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print('Generating embeddings...')
    embeddings = model.encode(text_to_embed, show_progress_bar=True)

    print('Saving embeddings...')
    np.save('../../data/all/embeddings.npy', embeddings)

    print(f'[INFO] : Saved {embeddings.shape[0]} embeddings with {embeddings.shape[1]} dimensions')


if __name__ == '__main__':
    generate_embeddings()