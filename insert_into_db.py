import pandas as pd
from sqlalchemy import create_engine


CATALOG_PATH = 'Catalogs/catalog_ready-2_0.xlsx'
DATA_PATH = 'generated_files/invoices_revised-2_0.xlsx'

# Database connection
engine = create_engine('mysql+mysqlconnector://<username>:<password>4@<host/ip>/<servername>')

# Read data 
df_catalog = pd.read_excel(CATALOG_PATH, sheet_name='CONSOLIDADA', engine='openpyxl')
df_invoice = pd.read_excel(DATA_PATH, engine='openpyxl')

# Process Invoice Item data
invoice_items_df = df_invoice[['Product_code', 'Sqm', 'Unit_price', 'Total_price', 'Currency', 'Invoice_number']]
invoice_items_df = invoice_items_df.rename(columns={
    'Product_code': 'product_code', 'Sqm': 'sqm', 
    'Unit_price': 'unit_price', 'Total_price': 'total_price', 
    'Currency': 'currency'
})

# Filter product catalog to exclude existing product codes
existing_product_codes = pd.read_sql("SELECT product_code FROM product", con=engine)['product_code'].tolist()
df_catalog_filtered = df_catalog[~df_catalog['product_code'].isin(existing_product_codes)]

# Insert new product data 
if not df_catalog_filtered.empty:
    df_catalog_filtered.to_sql('product', con=engine, index=False, if_exists='append')
    print('New product data inserted')

# Insert Customer data
customers_df = df_invoice[['Client', 'Country']].drop_duplicates().rename(columns={'Client': 'name', 'Country': 'country'})
customers_df.to_sql('customer', con=engine, index=False, if_exists='append')
print('Customer data inserted')

# Insert Invoice data 
customer_ids = pd.read_sql("SELECT customer_id, name FROM customer", con=engine)
invoice_df = df_invoice.merge(customer_ids, left_on='Client', right_on='name')
invoice_df = invoice_df[['Invoice_number', 'Date', 'FOB', 'Destination', 'customer_id']]
invoice_df = invoice_df.drop_duplicates(subset='Invoice_number')
invoice_df = invoice_df.rename(columns={'Date': 'issue_date', 'Destination': 'destination_port', 'FOB': 'fob'})
invoice_df.to_sql('invoice', con=engine, index=False, if_exists='append')
print('Invoice data inserted')

# Insert InvoiceItem data
invoice_items_df['product_code'] = invoice_items_df['product_code'].astype(str)
existing_product_codes = pd.read_sql("SELECT product_code FROM product", con=engine)['product_code'].tolist()
filtered_invoice_items_df = invoice_items_df[invoice_items_df['product_code'].isin(existing_product_codes)]
# Drop duplicates
filtered_invoice_items_df = filtered_invoice_items_df.drop_duplicates(subset=['Invoice_number', 'product_code'])

print("Rows in filtered_invoice_items_df after filtering and dropping duplicates:", len(filtered_invoice_items_df))

# Insert filtered InvoiceItem data
if not filtered_invoice_items_df.empty:
    filtered_invoice_items_df.to_sql('invoiceitem', con=engine, index=False, if_exists='append')
    print('Invoice item data inserted')
