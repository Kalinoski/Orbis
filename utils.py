import pandas as pd
from decimal import Decimal
from setup import CATALOGS_DIR_PATH


def read_and_preprocess_catalog():
    catalog = pd.read_csv(CATALOGS_DIR_PATH + 'CarmeloFior_catalog.csv')

    catalog['COD'] = catalog['COD'].apply(lambda x: ''.join(filter(str.isdigit, str(x))) if pd.notnull(x) else 'NaN')
    catalog['COD'] = catalog['COD'].apply(lambda x: x[:-1] if pd.notnull(x) else 'NaN')
    catalog['COD'] = catalog['COD'].str.zfill(5)

    return catalog


def to_float(value: str or float or int, precision: int = 2) -> Decimal:
    """
    Converts a string, float, or integer value to a Decimal with a specified precision. It handles
    values with different formats of decimal and thousands separators (either ',' or '.'). For example,
    it can handle values like '1,234.56', '1234,56', and '1.234,56'.

    Parameters:
    value (str or float or int): The value to be converted to a Decimal.
    precision (int, optional): The precision of the Decimal. Default is 2.

    Returns:
    Decimal: The converted value as a Decimal with the specified precision.
    """
    
    if type(value) != str:
        value = str(value)

    if '.' in value and ',' in value:
        if value.rfind('.') > value.rfind(','):
            value = value.replace(',', '')
        else:
            value = value.replace('.', '').replace(',', '.')
    else:
        if value.count('.') > 1 or (value.count('.') == 1 and value.rfind('.') < len(value) - 3):
            value = value.replace('.', '')
        elif value.count(',') > 1 or (value.count(',') == 1 and value.rfind(',') < len(value) - 3):
            value = value.replace(',', '')

        value = value.replace(',', '.')

    return Decimal(value)