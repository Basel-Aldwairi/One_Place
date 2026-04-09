import pandas as pd
import numpy as np
import ast


def clean_specs(specs_string):
    if specs_string == '{}' or pd.isna(specs_string):
        return ''

    try:
        specs_dict = ast.literal_eval(specs_string)

        key_specs = {'processor',
                     'memory',
                     'storage',
                     'graphic'}

        specs_list = []
        for k, v in specs_dict.items():
            k_set = set(k.lower().split())

            if not k_set.isdisjoint(key_specs) and 'number' not in k_set:
                specs_list.append(str(v).lower())

        cleaned_specs = ', '.join(specs_list)

        return cleaned_specs

    except Exception as e:
        print(e)
        return ''


def clean_categories(categories_string):

    if categories_string == '{}' or pd.isna(categories_string):
        return ''

    try:
        categories_set = ast.literal_eval(categories_string)

        cleaned_categories = str(categories_set).replace('\'', '').lower()[1:-1]

        return cleaned_categories

    except Exception as e:
        print(e)
        return ''


def preprocess_file(file_path):
    df = pd.read_csv(file_path, index_col=0)

    valid_df = df[df['in_stock'] == True].copy()

    valid_df['price'] = valid_df['price'].astype(np.float64)
    valid_df['original_price'] = valid_df['original_price'].fillna(valid_df['price'])

    valid_df = valid_df.drop(columns=['in_stock', 'currency'])

    valid_df['product_name'] = valid_df['product_name'].apply(str.lower)

    valid_df['brand'] = valid_df['brand'].apply(str.lower)

    valid_df['specs'] = valid_df['specs'].apply(clean_specs)

    valid_df['categories'] = valid_df['categories'].apply(clean_categories)

    valid_df.loc[valid_df['product_description'] == 'Unknown', 'product_description'] = 'No Description'

    model_text = (valid_df['brand'] + ' ' +
                  valid_df['product_name'] + ' ' +
                  valid_df['specs'])

    valid_df['model_text'] = model_text

    return valid_df


def combine_preprocess(paths_list):
    dfs = []
    for i in range(len(paths_list)):
        df = preprocess_file(paths_list[i])
        dfs.append(df)

    combined_df = pd.concat(dfs, axis=0, ignore_index=True)

    return combined_df

if __name__ == '__main__':
    paths_list = [
        '../data/compujordan/compujordan_products.csv',
        '../data/oriental_store/oriental_store_products.csv'
    ]

    combined_df = combine_preprocess(paths_list)
    combined_df.to_csv('../data/all/all_products.csv', index=False)