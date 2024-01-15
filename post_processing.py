import pandas as pd


def convert_foreign_date(date, month_dict):
    if isinstance(date, str):
        for month_abbr, replacement in month_dict.items():
            if month_abbr in date:
                date = date.replace(month_abbr, replacement)
                break
        return pd.to_datetime(date, format='%d-%b-%y', errors='coerce')
    else:
        return date
    
def convert_amount_to_float(amount):
    try:
        amount = amount.replace('.', '').replace(',', '.')
        return round(float(amount), 2)
    except:
        return round(amount, 2)

def filter_consecutive_invoices(df):
    df['Invoice_Change'] = df['Invoice_number'] != df['Invoice_number'].shift(1)
    df['Group'] = df['Invoice_Change'].cumsum()
    group_counts = df.groupby(['Invoice_number', 'Group']).size()
    max_groups = group_counts.reset_index().groupby('Invoice_number')[0].idxmax()
    valid_groups = group_counts.iloc[max_groups].index.get_level_values('Group')

    return df[df['Group'].isin(valid_groups)].drop(columns=['Invoice_Change', 'Group'])


df_original = pd.read_excel('generated_files/invoices_revised.xlsx')
df = df_original.copy()

spanish_to_english_months = {
    'Ene': 'Jan', 'Feb': 'Feb', 'Mar': 'Mar', 'Abr': 'Apr', 'May': 'May', 'Jun': 'Jun',
    'Jul': 'Jul', 'Ago': 'Aug', 'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Dic': 'Dec'
}

df['Date'] = df['Date'].apply(lambda x: convert_foreign_date(x, spanish_to_english_months))
df['Sqm'] = df['Sqm'].apply(convert_amount_to_float)
df['Unit_price'] = df['Unit_price'].apply(convert_amount_to_float)
df['Total_price'] = df['Total_price'].apply(convert_amount_to_float)
df['FOB'] = df['FOB'].apply(convert_amount_to_float)
df['Size'] = df['Size'].apply(lambda x: x.lower() if isinstance(x, str) else x)

filtered_df = filter_consecutive_invoices(df)

filtered_df.to_excel('generated_files/invoices_revised-2_0.xlsx', index=False)

