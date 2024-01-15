import pandas as pd
import re
from text_extraction import *
from collect_and_preprocess import find_cell_with_exact_content, merge_row_cells_with_below
from utils import read_and_preprocess_catalog, to_float


class Invoice:
    def __init__(self, file_name, catalog) -> None:
        """
        Initializes an Invoice instance.

        Processesing both PDF and DOCX versions of an invoice, extracting text, identifying key data points
        like invoice number, issue date, client name, etc., from the extracted text. It also processes product data,
        calculates amounts, and sets a flag for any discrepancies.
    
        Parameters:
        file_name (str): Name of the file.
        catalog (DataFrame): A catalog DataFrame.
        """

        self.pdf_file_name = file_name + '.pdf'
        self.docx_file_name = file_name + '.docx'

        self.text_pdf = get_text_from_pdf(self.pdf_file_name)
        self.lines_pdf = re.split('\n', self.text_pdf)

        docx_path = convert_pdf_to_docx(self.pdf_file_name)
        # self._preprocess_docx(docx_path)
        if docx_path:
            self.text_docx = extract_text_from_docx(docx_path)
        self.lines_docx = re.split('\n', self.text_docx)

        self.text_list_docx = extract_table_data_from_docx(self.docx_file_name)
        self.text_list_pdf = extract_table_data_from_pdf(self.pdf_file_name)

        self.invoice_number = self._get_data_based_on_keyword(['invoice number', 'invoice nr'], self.text_list_docx)
        self.issue_date = self._get_data_based_on_keyword(['issue date', 'fecha'], self.text_list_docx)
        self.client_name = self._get_data_based_on_keyword(['bill to', 'importador'], self.text_list_docx)
        self.currency = self._get_data_based_on_keyword(['currency', 'moneda'], self.text_list_docx)
        self.destination_port = self._get_data_based_on_keyword(['destination port', 'puerto de destino'], self.text_list_docx)
        self.products = self._get_products()
        self.products = self._get_product_names_and_sizes(catalog)

        self.sub_total_amount = 0
        self.fumigation = 0
        self.fob = 0
        self._get_amounts(['sub-total amount', 'sub-total', 'valor sub-total'])
        self.flag = False

    def _preprocess_docx(self, docx_path):
        """
        Preprocesses a DOCX file by merging cells with specific content in a table.
    
        Used to modify the table structure in a DOCX file, based on the presence of 
        specific content (e.g., 'Sqm', 'M2') in the table cells.
    
        Parameters:
        docx_path (str): The file path of the DOCX document.
        """

        locations = find_cell_with_exact_content(docx_path, target_string='Sqm')
        if locations == None:
            locations = find_cell_with_exact_content(docx_path, target_string='M2')

        if locations != None and len(locations) >= 2:
            merge_row_cells_with_below(docx_path, locations[0], locations[1], save_path=docx_path)

    def _get_data_based_on_keyword(self, keywords, list_text):
        """
        Extracts data based on a list of keywords from a given text list.
        Searches for each keyword in the text list and returns the text immediately following the 
        first occurrence of any of the keywords.
    
        Parameters:
        keywords (list): A list of keywords to search for in the text.
        list_text (list): The list of text lines to search through.
    
        Returns:
        str: The extracted data following the keyword or an empty string if not found.
        """

        for text in list_text:
            for keyword in keywords:
                if text.casefold().startswith(keyword):
                    return text[len(keyword):].strip()

        return ''

    def _get_products(self):
        """
        Extracts product information from the invoice document.
        Processes the document text to identify and extract product information such as product codes,
        quantities, unit prices, and total prices. It returns this information in a DataFrame format.
    
        Returns:
        DataFrame: A DataFrame containing product information extracted from the invoice.
        """

        lines = self.lines_docx
        # Remove whitespaces from the beggining of each line
        lines = [line.lstrip() for line in lines]

        start_strings = ['description of goods', 'descripcion de las mercancias']
        end_strings = ['signature', 'visto']

        # Find lines within start_string and end_string
        start_index = next(
            (i for i, s in enumerate(lines) for start_string in start_strings if s.lower().startswith(start_string)),
            None)
        end_index = next(
            (i for i, s in enumerate(lines) for end_string in end_strings if s.lower().startswith(end_string)), None)

        if start_index is not None and end_index is not None:
            lines = lines[start_index:end_index + 1]

        # Extract product codes
        code_list = [re.match(r'^(\d{5}|990).*', s).group(1) for s in lines if re.match(r'^(\d{5}|990).*', s)]

        # Get extract containing square meter quantities, unit prices and total prices
        sqm_extract = self._get_data_based_on_keyword(['sqm', 'm2'], self.text_list_docx)
        unit_prices_extract = self._get_data_based_on_keyword(['unit.price', 'precio un', 'prieco un'], self.text_list_docx)
        total_prices_extract = self._get_data_based_on_keyword(['total', 'importe'], self.text_list_docx)

        # Split string into parts using pattern that matches anything not a digit, comma, or period
        sqm_list = re.split(r'[^0-9.,]+', sqm_extract)
        unit_prices_list = re.split(r'[^0-9.,]+', unit_prices_extract)
        total_prices_list = re.split(r'[^0-9.,]+', total_prices_extract)

        # Remove empty strings resulting from the split
        sqm_list = [part for part in sqm_list if part]
        unit_prices_list = [part for part in unit_prices_list if part]
        total_prices_list = [part for part in total_prices_list if part]

        try:
            # Check if all lists have the same length
            if len(set(map(len, [code_list, sqm_list, unit_prices_list, total_prices_list]))) != 1:
                truncate_to_shortest(code_list, sqm_list, unit_prices_list, total_prices_list)

            df = pd.DataFrame({
                'Product_code': code_list,
                'Sqm': sqm_list,
                'Unit_price': unit_prices_list,
                'Total_price': total_prices_list
            })

            return df

        except ValueError as e:
            print(f'{self.invoice_number}: {e}')
            return pd.DataFrame()

    def _get_product_names_and_sizes(self, catalog):
        """
        Merges product data with additional information from a catalog.
        This method combines the extracted product data with a catalog to include additional details like product
        names and sizes. It returns a DataFrame with the merged information.
    
        Parameters:
        catalog (DataFrame): Product catalog dataframe.
    
        Returns:
        DataFrame: A dataframe with product information.
        """

        df = self.products

        df['Product_code'] = df['Product_code'].astype(str)

        merged_df = pd.merge(df, catalog, left_on='Product_code', right_on='COD', how='left')
        merged_df.rename(columns={'REFERÊNCIA': 'Product_name', 'TAMANHO': 'Size'}, inplace=True)

        df = merged_df[list(df.columns) + ['Product_name', 'Size']]
        cols_to_order = ['Product_code', 'Product_name', 'Size']
        df = df[cols_to_order + (df.columns.drop(cols_to_order).tolist())]

        return df

    def _get_amounts(self, keywords):
        """
        Extracts various monetary amounts from the invoice text based on given keywords.
        This method searches the text for specified keywords and extracts the monetary values that follow these
        keywords. 
    
        Parameters:
        keywords (list): A list of keywords to search for in the invoice text.
        """

        text = self.text_pdf
        text = text.lower()
        for keyword in keywords:
            index = text.find(keyword)
            if index != -1:
                text = text[index + len(keyword):]
                break

        if index == -1:
            return None

        print(text)
        if re.search(r'\.\d{1,3}\,', text):
            # Matches numbers using "." for thousands and "," for decimals
            pattern = r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?)'
        else:
            # Matches numbers using "," for thousands and "." for decimals
            pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'

        amounts = re.findall(pattern, text)
        print(amounts)
        self.sub_total_amount = amounts[0] if len(amounts) > 0 else None
        self.fumigation = amounts[1] if len(amounts) > 2 else None
        if len(amounts) == 2:
            self.fob = amounts[1]
        elif len(amounts) > 2:
            self.fob = amounts[2]
        else:
            self.fob = None


def main():
    """
    Reads and preprocesses a catalog; iterates through each PDF file in the specified directory;
    processes each file as an invoice; Performs various calculation; 
    Identifies discrepancies between calculated subtotals and the sum of product prices, flags these invoices, and then 
    compiles the data from all processed invoices into a single DataFrame. This DataFrame is then saved to a CSV file.
    """

    catalog = read_and_preprocess_catalog()

    files = [f for f in os.listdir(PDFs_DIR_PATH) if os.path.isfile(os.path.join(PDFs_DIR_PATH, f))]
    invoices = []
    invoice_numbers = []
    flags = 0
    broken_invoices = []
    for i, file in enumerate(files):
        file = re.sub(r'\..*', '', file)
        print(f'Processing file: {file}')
        invoices.append(Invoice(file, catalog))

        df = invoices[i].products.copy()
        df['Total_price'] = df['Total_price'].apply(to_float)
        sub_total_amount = to_float(invoices[i].sub_total_amount)
        price_sum = df['Total_price'].sum()
        if sub_total_amount != price_sum:
            df = df.drop_duplicates(subset='Product_code', keep='first')
            price_sum = df['Total_price'].sum()
            if sub_total_amount != price_sum:
                flags += 1
                broken_invoices.append(invoices[i])
                invoices[i].flag = True
                print(f'sub-total amount - {str(sub_total_amount)} is different then SUM of products - {str(price_sum)}')
            else:
                invoices[i].products = df

        print(f'Done: {file}')
        print(f'[{i} / {len(files)}] - done')

    print(f'\nflags: {flags}')  

    test = broken_invoices[0].fob

    # Build final frame:
    df = pd.DataFrame()
    for invoice in invoices:
        if invoice.flag:
            continue
        df_invoice = invoice.products
        df_invoice['Invoice_number'] = invoice.invoice_number
        df_invoice['Client'] = invoice.client_name
        df_invoice['Date'] = invoice.issue_date
        df_invoice['Currency'] = invoice.currency
        df_invoice['Destination'] = invoice.destination_port
        df_invoice['FOB'] = invoice.fob
        df = pd.concat([df, df_invoice], axis=0).reset_index(drop=True)

    df.to_csv('C:/All/PyProjects/Orbis/invoices.csv', index=False)

if __name__ == "__main__":
    main()

   
    



