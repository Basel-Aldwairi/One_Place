import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from rapidfuzz import fuzz, process


def combine_indicies(search_method_indicies_list):

    combined_dict = {}

    for search_method_indicies in search_method_indicies_list:
        for rank, index in enumerate(search_method_indicies):
            if index not in combined_dict:
                combined_dict[index] = 0
            combined_dict[index] += 1 / (rank + 1)

    return combined_dict


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

    def fuzzy_search(self,query):
        code_matchs = process.extract(query, self.products_df['product_code'].to_list(), limit=top_k)

        relevant_codes = {code for code, score, _ in code_matchs if score >= 80}

        item_indicies = []
        if relevant_codes:
            for code in relevant_codes:
                item_index = self.products_df[self.products_df['product_code'] == code].index.tolist()
                for idx in item_index:
                    item_indicies.append(idx)

                # for idx in range(len(items_df)):
                #     item = items_df.iloc[idx].to_dict()
                #     items.append(item)

            return self.get_items(item_indicies)
        return None

    def faiss_search(self,query):

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

        return filtered_faiss_indices


    def bm25_search(self,query):

        tokenized_query = query.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_indices = np.argsort(bm25_scores)[::-1][:top_k]

        filtered_bm25_indices = []
        max_score = bm25_scores[bm25_indices[0]]
        accepnted_score = max_score * 0.9
        for index in bm25_indices:
            if bm25_scores[index] > accepnted_score:
                filtered_bm25_indices.append(index)

        return filtered_bm25_indices


    def multi_vendor_search(self,combined_indicies):

        expanded_indices = {}

        for index in combined_indicies.keys():
            index_product_code = self.products_df['product_code'].iloc[index]

            product_indicies = self.products_df[self.products_df['product_code'] == index_product_code].index
            rank = combined_indicies[index]

            for idx in product_indicies:
                if idx not in expanded_indices:
                    expanded_indices[idx] = rank

        return expanded_indices


    def get_items(self, indices):
        items = []
        for index in indices:
            item = self.products_df.iloc[index].to_dict()
            items.append(item)

        return items

    def search_query(self,query, top_k = 5):


        items = self.fuzzy_search(query)

        if items:
            return items

        query = query.lower()


        # print('Embeddings query...')

        faiss_indices = self.faiss_search(query)

        bm25_indices = self.bm25_search(query)

        combined_indicies = combine_indicies([faiss_indices, bm25_indices])

        expanded_indices = self.multi_vendor_search(combined_indicies)

        ranked_indices = sorted(expanded_indices.keys(), key=lambda x: expanded_indices[x], reverse=True)

        items = self.get_items(ranked_indices)

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