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


        code_matchs = process.extract(query, self.products_df['product_code'].to_list(), limit=top_k)
        # print(code_matchs)
        relevant_codes = [code for code, score, _ in code_matchs if score >= 90]

        items = []
        if relevant_codes:
            for code in relevant_codes:
                item = self.products_df[self.products_df['product_code'] == code].to_dict()
                items.append(item)
            return items

        query = query.lower()


        # print('Embeddings query...')
        query_vector = self.model.encode([query])

        # print('Searching...')
        distances, faiss_indices_nested = self.index.search(query_vector, top_k)
        faiss_indices = faiss_indices_nested[0]
        # print(f'{distances = }')


        faiss_distance_cutoff = 0.8

        filtered_faiss_indices = []
        for index in range(top_k):
            if distances[0][index] > faiss_distance_cutoff:
                break
            filtered_faiss_indices.append(faiss_indices[index])

        # print(f'{filtered_faiss_indices = }')


        tokenized_query = query.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_indices = np.argsort(bm25_scores)[::-1][:top_k]
        # print(f'{bm25_scores[bm25_indices] = }')
        # print(f'{bm25_indices = }')

        filtered_bm25_indices = []
        max_score = bm25_scores[bm25_indices[0]]
        accepnted_score = max_score * 0.9
        for index in bm25_indices:
            if bm25_scores[index] > accepnted_score:
                filtered_bm25_indices.append(index)

        # print(f'{filtered_bm25_indices = }')

        combined_indicies = {}

        for rank, index in enumerate(filtered_faiss_indices):
            if index not in combined_indicies:
                combined_indicies[index] = 0
            combined_indicies[index] += 1 / (rank + 1)

        for rank, index in enumerate(filtered_bm25_indices):
            if index not in combined_indicies:
                combined_indicies[index] = 0
            combined_indicies[index] += 1 / (rank + 1)

        expanded_indices = {}

        for index in combined_indicies.keys():
            index_product_code = self.products_df['product_code'].iloc[index]

            product_indicies = self.products_df[self.products_df['product_code'] == index_product_code].index
            rank = combined_indicies[index]
            # print(f'{product_indicies = }')

            for idx in product_indicies:
                if idx not in expanded_indices:
                    expanded_indices[idx] = rank

        ranked_indices = sorted(expanded_indices.keys(), key=lambda x: expanded_indices[x], reverse=True)

        for index in ranked_indices:
            item = self.products_df.iloc[index].to_dict()
            items.append(item)

        return items




if __name__ == '__main__':

    se = SearchEngine()
    top_k = 5

    while True:
        query = input('> ')
        if query == 'quit':
            quit()
        elif query == '.':
            top_k = int(input('new top_k >  '))

        else:
            items = se.search_query(query, top_k=top_k)

            for item in items:
                print(item)

