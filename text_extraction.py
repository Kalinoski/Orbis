import PyPDF2
from pdf2docx import Converter
import docx2txt
import pdfplumber
from docx import Document
import os
import re
import pandas as pd
from setup import PDFs_DIR_PATH, DOCS_DIR_PATH


def get_text_from_pdf(file_name: str) -> str:
    """
    Extracts text from a PDF file, returning the text from all pages.
    
    Parameters:
    file_name (str): The name of the PDF file.

    Returns:
    str: Text extracted from the PDF file.
    """

    file_path = PDFs_DIR_PATH + file_name
    pdf_text = ''
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            for page_number in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_number]
                pdf_text += page.extract_text()

    except FileNotFoundError:
        print(f'The file {file_path} does not exist.')
    except Exception as e:
        print(f'An unexpected error with the file {file_path} occurred: {str(e)}')

    return pdf_text


def convert_pdf_to_docx(pdf_file_name: str) -> str or None:
    """
    Converts a PDF file to a DOCX file.

    Parameters:
    pdf_file_name (str): The name of the PDF file to be converted.

    Returns:
    str or None: The path to the converted DOCX file, or None if an error occurs.
    """

    pdf_file_path = PDFs_DIR_PATH + pdf_file_name
    docx_file_name = pdf_file_name.replace('pdf', 'docx')
    docx_file_path = DOCS_DIR_PATH + docx_file_name

    if not os.path.isfile(docx_file_path):
        try:
            file = Converter(pdf_file_path)
            file.convert(docx_file_path)
            file.close()
        except Exception as e:
            print(f'An unexpected error with the file {pdf_file_path} occurred: {str(e)}')
            return None
        else:
            print(f'{os.path.splitext(pdf_file_name)[0]} - File Converted Successfully')
            return docx_file_path
    return docx_file_path


def extract_text_from_docx(docx_file_path: str) -> str:
    """
    Extracts text from a DOCX file and returns it as a string. Extra line breaks are removed.

    Parameters:
    docx_file_path (str): The file path of the DOCX document.

    Returns:
    str: The extracted text from the DOCX file.
    """

    text_docx = docx2txt.process(docx_file_path)
    text_docx = re.sub('\n+', '\n', text_docx)
    return text_docx


def get_table_from_pdf(file_name: str) -> pd.DataFrame:
    """
    Extracts the first table from a PDF file and returns it as a pandas DataFrame.

    Parameters:
    file_name (str): The name of the PDF file.
    
    Returns:
    pd.DataFrame: A DataFrame containing the extracted table data.
    """

    file_path = PDFs_DIR_PATH + file_name
    table_settings = {
        'vertical_strategy': 'text',
        'horizontal_strategy': 'lines'
    }

    pdf = pdfplumber.open(file_path)
    table = pdf.pages[0].extract_table(table_settings)
    df = pd.DataFrame(table[1::], columns=table[0])

    return df


def extract_table_data_from_docx(file_name: str) -> list:
    """
    Extracts and returns all unique text data from every cell in all tables within a DOCX file.

    Parameters:
    file_name (str): The name of the DOCX file.

    Returns:
    list: A list of unique cell texts from all tables in the DOCX file.
    """

    document = Document(DOCS_DIR_PATH + file_name)

    table_data = []
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                table_data.append(cell.text)

    table_data = list(dict.fromkeys(table_data))
    return table_data


def extract_table_data_from_pdf(file_name: str) -> list:
    """
    Extracts and returns all unique text data from every cell in all tables within a PDF file.

    Parameters:
    file_name (str): The name of the PDF file.

    Returns:
    list: A list of unique cell texts from all tables in the PDF file.
    """

    with pdfplumber.open(PDFs_DIR_PATH + file_name) as pdf:
        all_text = []
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                for row in table:
                    for cell in row:
                        all_text.append(cell)

        all_text = list(set(all_text))
        return all_text


def truncate_to_shortest(*lists) -> None:
    """
    Truncates all input lists to the length of the shortest list among them.

    Parameters:
    *lists: A variable number of list arguments.
    """

    # Get the length of the shortest list
    min_length = min(len(lst) for lst in lists)

    # Truncate each list to the length of the shortest list
    for lst in lists:
        del lst[min_length:]




