import pandas as pd
import os
import json
import time

# Paths
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, '..', '..', 'data', 'all', 'all_products.csv')

df = pd.read_csv(csv_path)


def count_categories(category: set, name):
    """
    Counts the number of the entries in the dataset with specific categories
    """

    start_time = time.time()

    counter = 0

    # Interate over all entries and count
    for i in range(len(df)):
        item = df.loc[i]
        categories = str(item['categories']).lower()

        # Check categories
        for c in category:
            if c in categories:
                counter += 1

    end_time = time.time()

    # Logging
    print(f'{name}: {counter}')
    print(f'finished in {end_time - start_time:.2f} seconds')
    print()

    return counter


def categories_barchart():
    """
    Calculate the number of entries in each category, to be
    displayed in the UI as a barchart

    saves the output to a JSON file for optimization
    """

    print('Counting categories...')

    # All categories
    categories = [
        {'cpu', 'processor'},
        {'gpu', 'graphics'},
        {'ram', 'memory'},
        {'ssd', 'hdd', 'storage'},
        {'power supply', 'psu'},
        {'motherboard'},
    ]

    # Category lists
    categories_name = ['CPUs', 'GPUs', 'RAM', 'Storage', 'Power Supplies', 'Motherboards']
    categories_count = []

    # Check each category and each item
    for i, c in enumerate(categories):
        name = categories_name[i]
        categories_count.append(count_categories(c, name))

    # Aggregate results
    json_dict = {
        'categories': categories_name,
        'count': categories_count,
    }

    # Save to JSON
    with open('insight_date/categories_count.json', 'w') as f:
        json.dump(json_dict, f)

    print('Saved categories_count.json')


def count_brands():
    """
    Count number of prodcuts each brand has

    Saves to a JSON file for optimization
    """
    print('Counting brands...')

    # Counting dictionary
    brand_count_search = {}

    # Loop over all products, and increament the dictionary
    for i in range(len(df)):

        brand = str(df.loc[i]['brand'])

        if brand in brand_count_search:
            brand_count_search[brand] += 1
        else:
            brand_count_search[brand] = 1

    # List of brand names and thier counts
    brand_names = list(brand_count_search.keys())
    brand_counts = list(brand_count_search.values())

    counts = brand_counts.copy()

    # Get heighest numbers of products
    counts.sort(reverse=True)
    valid_brands_count = 20
    cutoff = counts[valid_brands_count]

    # Get the brands with the heighest number of products
    valid_brands = [brand for brand in brand_names if brand_count_search[brand] >= cutoff]

    # Get the number of products for the filtered brand lists
    valid_counts = [brand_count_search[brand] for brand in valid_brands]
    total_valid_counts = sum(valid_counts)
    other_count = len(df) - total_valid_counts

    # The remaing products are set to Other
    valid_brands.append('other')
    valid_counts.append(other_count)

    # Aggregate results
    json_dict = {
        'brands': valid_brands,
        'count': valid_counts,
    }

    # Save to JSON
    with open('insight_date/brand_count.json', 'w') as f:
        json.dump(json_dict, f)

    print(f'Saved brand_counts.json')


if __name__ == '__main__':


    # Option choice
    option = input('Enter option: ')

    if option == 'h':
        print('1. count categories')
        print('2. count vendors')
        print('3. count brands')

    if option == '1':
        categories_barchart()

    if option == '2':
        count_brands()
