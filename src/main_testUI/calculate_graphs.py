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
    valid_brands = [brand for brand in brand_names if brand_count_search[brand] >= cutoff and brand != 'unknown']

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


def calculate_in_stock():

    print('Calculating in stock...')

    in_stock_count = len(df[df['in_stock'] == True])
    out_of_stock_count = len(df) - in_stock_count

    names = ['In Stock', 'Out of Stock']
    values = [in_stock_count, out_of_stock_count]

    json_dict = {
        'names': names,
        'values': values
    }

    with open('insight_date/in_stock_count.json', 'w') as f:
        json.dump(json_dict, f)

    print(f'Saved in_stock_counts.json')

def calculate_vendors():

    print('Calculating vendors...')

    vendors = list(df['store'].unique())

    counts = []
    for vendor in vendors:
        count = len(df[df['store'] == vendor])
        counts.append(count)

    json_dict = {
        'vendors': vendors,
        'counts': counts
    }

    with open('insight_date/vendors_count.json', 'w') as f:
        json.dump(json_dict, f)

    print(f'Saved vendors_counts.json')


def calculate_discounts_count():

    print('Calculating discounts...')

    discounts_count = len(df[(df['price'] < df['original_price']) & (df['in_stock'] == True)])
    not_discounts_count = len(df[df['in_stock'] == True]) - discounts_count

    names = ['Discounts', 'No Discounts']
    values = [discounts_count, not_discounts_count]

    json_dict = {
        'names': names,
        'values': values
    }

    with open('insight_date/discounts_count.json', 'w') as f:
        json.dump(json_dict, f)

    print(f'Saved discounts_counts.json')


def calculate_discounts_histogram():
    print('Calculating discounts histogram...')

    discounted_df = df[(df['price'] < df['original_price']) & (df['in_stock'] == True)]

    discounts_count = len(discounted_df)
    prices = list(discounted_df['price'])
    discounts = list(discounted_df['original_price'] - prices)

    percentages = []

    for i in range(discounts_count):
        percentage = (prices[i] - discounts[i]) / 100
        if percentage > 0:
            percentages.append(percentage)

    json_dict = {
        'percentages': percentages
    }

    with open('insight_date/discounts_histogram.json', 'w') as f:
        json.dump(json_dict, f)

    print(f'Saved discounts_histogram.json')


def in_stock_per_store():

    os_stock = df[(df['store'] == 'Oriental Store') & (df['in_stock'] == True)]
    os_stock_count = len(os_stock)

    os_count = len(df[df['store'] == 'Oriental Store'])

    print(f'{os_stock_count} Oriental Stores')

    cc_stock = df[(df['store'] == 'City Center') & (df['in_stock'] == True)]
    cc_stock_count = len(cc_stock)

    cc_count = len(df[df['store'] == 'City Center'])

    print(f'{cc_stock_count} City Centers')


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

    if option == '3':
        calculate_in_stock()

    if option == '4':
        calculate_vendors()

    if option == '5':
        calculate_discounts_count()

    if option == '6':
        calculate_discounts_histogram()

    if option == '7':
        in_stock_per_store()