import pandas as pd


file_path = 'generated_files/invoices_revised-2_0.xlsx'
invoices_df = pd.read_excel(file_path, engine='openpyxl')

start_date = pd.Timestamp('2022-07-01')
end_date = pd.Timestamp('2023-07-31')
eligible_start_date = pd.Timestamp('2022-07-01')
eligible_end_date = pd.Timestamp('2023-01-01')
exclusion_start_date = pd.Timestamp('2023-01-01')
exclusion_end_date = pd.Timestamp('2023-07-31')

# Filter Active Clients 
active_clients_df = invoices_df[
    (invoices_df['Date'] >= start_date) & (invoices_df['Date'] <= end_date)
]

# Determine Eligible Products for Each Client and Exclude Recent Purchases
client_reorder_suggestions = {}

for client in active_clients_df['Client'].unique():
    client_data = invoices_df[invoices_df['Client'] == client]

    # Products purchased by the client more than 6 months ago but less than a year ago
    eligible_products_client = set(client_data[
        (client_data['Date'] >= eligible_start_date) & (client_data['Date'] < eligible_end_date)
    ]['Product_code'].unique())

    # Products purchased by the client in the last 6 months
    excluded_products_client = set(client_data[
        (client_data['Date'] >= exclusion_start_date) & (client_data['Date'] <= exclusion_end_date)
    ]['Product_code'].unique())

    # Products eligible for reorder suggestion for the client
    reorder_products = list(eligible_products_client - excluded_products_client)

    client_reorder_suggestions[client] = reorder_products


reorder_suggestions_df = pd.DataFrame(list(client_reorder_suggestions.items()), columns=['Client', 'Reorder Suggestions'])

# Mapping from Product_code to Product_name merged with Size
product_name_size_map = {
    row['Product_code']: f"{row['Product_name']} {row['Size']}"
    for _, row in invoices_df[['Product_code', 'Product_name', 'Size']].drop_duplicates().iterrows()
}

# Modify client_reorder_suggestions to use product names instead of codes
for client in client_reorder_suggestions:
    client_reorder_suggestions[client] = [
        product_name_size_map.get(product_code, "Unknown Product")
        for product_code in client_reorder_suggestions[client]
    ]

# Replace client names with auto incremented numbers
client_ids = {client: idx for idx, client in enumerate(client_reorder_suggestions.keys(), start=1)}

modified_reorder_suggestions_df = pd.DataFrame([
    {"Client ID": client_ids[client], "Reorder Suggestions": suggestions}
    for client, suggestions in client_reorder_suggestions.items()
])

modified_reorder_suggestions_df['Reorder Suggestions'] = modified_reorder_suggestions_df['Reorder Suggestions'].apply(lambda x: x[:5])
modified_reorder_suggestions_df.to_csv('C:/All/PyProjects/Orbis/generated_files/reorder_suggestion.csv', index=False)






