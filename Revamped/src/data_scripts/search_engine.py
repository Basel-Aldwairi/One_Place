import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from rapidfuzz import fuzz, process


class SearchEngine:

    def __init__(self):
        print('Reading files...')
        self.products_df = pd.read_csv('../../data/all/all_products.csv', index_col=0)
        self.embeddings = np.load('../../data/all/embeddings.npy')

        dimensions = self.embeddings.shape[1]
        print('Creating FAISS vectors...')

        self.index = faiss.IndexFlatL2(dimensions)
        self.index.add(self.embeddings)

        tokenized_corpus = [str(corpus).split() for corpus in self.products_df['model_text'].to_list()]
        self.bm25 = BM25Okapi(tokenized_corpus)


        print('Loading model...')
        self.model = SentenceTransformer('all-MiniLM-L6-v2')




    def search_query(self,query, top_k = 5):

        query = query.lower()

        print('Embeddings query...')
        query_vector = self.model.encode([query])

        print('Searching...')
        distances, faiss_indices_nested = self.index.search(query_vector, top_k)
        faiss_indices = faiss_indices_nested[0]
        print(f'{distances = }')

        tokenized_query = query.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_indices = np.argsort(bm25_scores)[::-1][:top_k]
        print(f'{bm25_scores[bm25_indices] = }')

        combined_indices = set(faiss_indices).union(set(bm25_indices))


        items = []
        for index in combined_indices:
            item = self.products_df.iloc[index].to_dict()

            items.append(item)

        items.sort(key=lambda x: x['price'], reverse=False)

        return items




if __name__ == '__main__':

    se = SearchEngine()

    while True:
        query = input('> ')
        if query == 'quit':
            quit()
        if query == '.':
            query = 'razer wireless mouse'

        items = se.search_query(query)

        for item in items:
            print(item)

