import pandas as pd


# Code for masking client names (replacing them with unique numbers)
DIR_PATH = 'C:/All/PyProjects/Orbis/'
FILE_NAME = 'invoices.csv'

df = pd.read_csv(DIR_PATH + FILE_NAME)

unique_customers = df['Client'].unique()

df_customers = pd.DataFrame({'name': unique_customers})

df_customers['customer_id'] = range(1, len(df_customers) + 1)

df_customers.to_csv(DIR_PATH + 'customers.csv', index=False)