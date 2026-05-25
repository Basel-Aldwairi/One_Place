import pandas as pd
import numpy as np
import ast
import time


# Cleaning Specs columns
# Turn a string of a dictionary into a string that can be used to calculate the embedding vector
def clean_specs(specs_string):

    # Return empty string if empty dictionary or NaN
    if specs_string == '{}' or pd.isna(specs_string):
        return ''

    try:
        # Turn String of a dictionary into a python dictionary
        specs_dict = ast.literal_eval(specs_string)

        # Specs that we filter in
        key_specs = {'processor', 'cpu', #CPU specs
                     'memory', 'ram', # RAM specs
                     'storage', 'ssd', 'hdd', # SSD | HDD specs
                     'graphic', 'gpu',} # GPU specs

        # Filtered specs
        specs_list = []
        # Iterate over all specs
        for k, v in specs_dict.items():
            # Get each word of the key
            k_set = set(k.lower().split())
            # If the key contains a word that indicated a wanted spec, we add the value to the filtered specs
            # Filter out specs with the word number, as most of them are as number of ram sticks which clutter the final
            # string
            if not k_set.isdisjoint(key_specs) and 'number' not in k_set:
                specs_list.append(str(v).lower())

        # Turn list of specs into a string
        cleaned_specs = ', '.join(specs_list)

        # Return specs string
        return cleaned_specs

    except Exception as e:
        print(e)
        return ''

# Cleaning categories column
# Turn a string of a set into a string that can be used to calculate the embedding vector
# Note : Not used in embeddings
def clean_categories(categories_string):

    # Return empty string if empty set or NaN
    if categories_string == '{}' or pd.isna(categories_string):
        return ''

    try:
        # Turn String of a set into a python set
        categories_set = ast.literal_eval(categories_string)


        # Turn set into a dictionary
        cleaned_categories = str(categories_set)
        # Remove stray '
        cleaned_categories = cleaned_categories.replace('\'', '')
        # Lowercasing the string for normalization
        cleaned_categories = cleaned_categories.lower()
        # Removing { and }
        cleaned_categories = cleaned_categories[1:-1]

        # Return cleaned categories
        return cleaned_categories

    except Exception as e:
        print(e)
        return ''


# Preprocess a products CSV that was scraped with a scraper
# Returns a Pandas DataFrame
def preprocess_file(file_path):

    # Read CSV file
    df = pd.read_csv(file_path)

    # Filter out all the out-of-stock products
    # valid_df = df[df['in_stock'] == True].copy()
    valid_df = df.copy()

    # Ensure the price is of type float64
    valid_df['price'] = valid_df['price'].astype(np.float64)
    # If original price is empty, meaning that the product is not on sale. Fill with price
    # Note : 'price' is the current price of a products, whether it's on sale or not
    # Note : 'original_price' is the price of the product before sale if the item is on sale, otherwise it is empty
    # so we fill it
    valid_df['original_price'] = valid_df['original_price'].fillna(valid_df['price'])

    # Drop the 'in_stock' and 'currency' columns
    # 'in_stock', has been used for filtering
    # 'currency', all prices are in JOD during scraping
    valid_df = valid_df.drop(columns=[ 'currency'])

    # Lowercasing the 'product_name' and 'brand' columns, to be used in embeddings
    valid_df['product_name'] = valid_df['product_name'].apply(str.lower)
    valid_df['brand'] = valid_df['brand'].apply(str.lower)

    # Clean 'specs' and turn into a string to be used in embeddings
    valid_df['specs'] = valid_df['specs'].apply(clean_specs)

    # Clean 'categories', was originally planned to be used in embeddings, but was dropped after testing
    valid_df['categories'] = valid_df['categories'].apply(clean_categories)

    # Clean 'product_description', turn 'Unknown' into a more comprehensable 'No Description'
    valid_df.loc[valid_df['product_description'] == 'Unknown', 'product_description'] = 'No Description'

    # Concatenate the features that will be used in embeddings
    model_text = (valid_df['product_name'] + ' ' +
                  valid_df['specs'] + ' ' +
                    valid_df['categories'])

    # Add embeddings text into the DataFrame
    valid_df['model_text'] = model_text

    # Return the preprocessed DataFrame
    return valid_df


# Combines all products from all scraped stores after preprocessing each file
def combine_preprocess(paths_list):

    # List of DataFrames that will be combined
    dfs = []

    # Iterate over each file, preprocess it and add it to the list of DataFrames
    for i in range(len(paths_list)):
        preprocess_time = time.time()

        # Get name and file path
        store_name = paths_list[i][0]
        store_path = paths_list[i][1]

        # Preprocess file of a store
        df = preprocess_file(store_path)

        # Append to the list of DataFrames
        dfs.append(df)

        # Info printing
        preprocess_time = time.time() - preprocess_time
        print(f'Finished preprocessing {store_name} in {preprocess_time:.5f} seconds')

    # Combine all DataFrames together
    combined_df = pd.concat(dfs, axis=0, ignore_index=True)

    # Return the combined DataFrame
    return combined_df

# Main script run
if __name__ == '__main__':
    paths_list = [
        ('City Center','../../data/citycenter/city_center_products.csv'),
        ('Oriental Store','../../data/oriental_store/oriental_store_products.csv')
    ]

    # Calculate time of the preprocessing and combinations step
    preprocessing_time = time.time()

    # Preprocess and combine all stores
    combined_df = combine_preprocess(paths_list)

    preprocessing_time = time.time() - preprocessing_time

    # Infos printing
    print(f'Finished preprocessing in {preprocessing_time:.5f} seconds')

    # Saving the finalized DataFrame
    finalized_file_path = '../../data/all/all_products.csv'
    combined_df.to_csv(finalized_file_path)