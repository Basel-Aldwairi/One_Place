import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from rapidfuzz import fuzz, process
import os
import time



class SearchEngine:

    FUZZY_SEARCH = 0
    FAISS_SEARCH = 1
    BM25_SEARCH = 2


    def __init__(self, static=False):

        start_time = time.time()

        base_dir = os.path.dirname(os.path.abspath(__file__))

        csv_path = os.path.join(base_dir, '..', '..', 'data', 'all', 'all_products.csv')
        embeddings_path = os.path.join(base_dir, '..', '..', 'data', 'all', 'embeddings.npy')
        model_path = os.path.join(base_dir, '..', 'models', 'embeddings_model')

        self.products_df = pd.read_csv(csv_path)

        if not static:
            print('Reading files...')
            # self.products_df = pd.read_csv(csv_path, index_col=0)
            self.embeddings = np.load(embeddings_path)

            dimensions = self.embeddings.shape[1]
            print('Creating FAISS vectors...')

            self.index = faiss.IndexFlatL2(dimensions)
            self.index.add(self.embeddings)

            tokenized_corpus = [str(corpus).split() for corpus in self.products_df['model_text'].to_list()]
            self.bm25 = BM25Okapi(tokenized_corpus)

            print('Loading model...')
            self.model = SentenceTransformer(model_path)


        end_time = time.time()
        initialization_time = end_time - start_time
        print('Initialization time:', initialization_time)
        # print(self.products_df.head())

    def fuzzy_search(self, query, top_k=10):
        code_matchs = process.extract(query, self.products_df['product_code'].to_list(), limit=top_k)

        relevant_codes = {code : score for code, score, _ in code_matchs if score >= 90}

        # print(relevant_codes)
        codes_ranked = sorted(relevant_codes.keys(), key= lambda x : relevant_codes[x], reverse=True)
        # print(codes_ranked)

        item_indicies = []
        if relevant_codes:
            for code in relevant_codes:
                item_index = self.products_df[self.products_df['product_code'] == code].index.tolist()
                for idx in item_index:
                    item_indicies.append(idx)

                # for idx in range(len(items_df)):
                #     item = items_df.iloc[idx].to_dict()
                #     items.append(item)

            return item_indicies
        return None

    def faiss_search(self, query, top_k):

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

    def bm25_search(self, query, top_k):

        tokenized_query = query.split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_indices = np.argsort(bm25_scores)[::-1][:top_k]

        filtered_bm25_indices = []
        max_score = bm25_scores[bm25_indices[0]]
        accepnted_score = max_score * 0.9
        accepted_scores = []
        accepted_scores.append(max_score)
        for index in bm25_indices:
            if bm25_scores[index] > accepnted_score:
                filtered_bm25_indices.append(index)
                accepted_scores.append(bm25_scores[index])

        print(f'{accepted_scores = }')
        return filtered_bm25_indices

    def combine_indicies(self, search_method_indicies_list):

        combined_dict = {}

        for search_type, search_method_indicies in enumerate(search_method_indicies_list):
            if not search_method_indicies:
                continue

            for rank, index in enumerate(search_method_indicies):
                if index not in combined_dict:
                    combined_dict[index] = 0
                combined_dict[index] += 1 / (rank + 1)

                if self.products_df.iloc[index]['in_stock'] == True:
                    combined_dict[index] += 0.5

                if search_type == self.FUZZY_SEARCH:
                    combined_dict[index] += 1

        return combined_dict

    def multi_vendor_search(self, combined_indicies):

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

        gaming_builds_items = []
        for index in indices:
            item = self.products_df.iloc[index].to_dict()
            item.pop('Unnamed: 0', None)
            if item['product_code'] not in {'GAMING BUILD', 'OS BUILD'}:
                items.append(item)

            else:
                gaming_builds_items.append(item)

        if gaming_builds_items:
            for item in gaming_builds_items:
                items.append(item)

        return items

    def filter_in_stock(self, items: list[dict]):
        in_stock_items = []

        for item in items:
            if item['in_stock'] == True:
                in_stock_items.append(item)

        return in_stock_items

    def filter_price(self,items :list[dict], min_price:int = 0, max_price : int = 999999):

        valid_items = []

        for item in items:
            item_price = item['price']
            if min_price <= item_price <= max_price:
                valid_items.append(item)

        return valid_items


    def search_query(self, query: str, top_k: int = 5, in_stock_only: bool = True, min_price: int = 0,
                     max_price: int = 999999, selected_models = None):

        if not selected_models:
            selected_models = {self.FUZZY_SEARCH, self.FAISS_SEARCH, self.BM25_SEARCH}

        query = query.strip()

        fuzzy_indicies = self.fuzzy_search(query, top_k) if self.FUZZY_SEARCH in selected_models else None

        query = query.lower()

        # print('Embeddings query...')

        faiss_time = time.time()
        faiss_indices = self.faiss_search(query, top_k) if self.FAISS_SEARCH in selected_models else None
        faiss_time = time.time() - faiss_time

        bm25_time = time.time()
        bm25_indices = self.bm25_search(query, top_k) if self.BM25_SEARCH in selected_models else None
        bm25_time = time.time() - bm25_time

        combined_indicies = self.combine_indicies([fuzzy_indicies,faiss_indices, bm25_indices])

        expanded_indices = self.multi_vendor_search(combined_indicies)

        ranked_indices = sorted(expanded_indices.keys(), key=lambda x: expanded_indices[x], reverse=True)

        items = self.get_items(ranked_indices)

        items = self.filter_price(items, min_price, max_price)

        print(f'{faiss_time = }')
        print(f'{bm25_time = }')

        if in_stock_only:
            in_stock_items = self.filter_in_stock(items)
            return in_stock_items
        else:
            return items

    def search_static(self, query, top_k=5):

        indicies_list = list(range(top_k))

        items = self.get_items(indicies_list)

        return items


if __name__ == '__main__':

    se = SearchEngine()
    top_k = 5
    in_stock_only = True

    while True:
        query = input('> ')
        if query == 'quit':
            quit()
        elif query == '.':
            top_k = int(input('new top_k >  '))
        elif query == ',':
            in_stock_only = not in_stock_only
            print(f'{in_stock_only = }')

        else:
            items = se.search_query(query, top_k=top_k, in_stock_only=in_stock_only)

            for item in items:
                print(item)
