This project contains the source code used for our engineering diploma project at Gdansk University of Technology.

Thesis title: Automating data for operational efficiency in a Brazilian SME.

The Brazilian SME is a company called Oribs Export, responsible for representing Brazilian and Spanish ceramic tiles factories by sellings their products to clients around the Americas.

In our methodological steps, we developed Python scripts to handle automated invoice data extraction, SQL code for creating tables, a pipeline for deploying data into the database and DAX queries for creating customized measures in PowerBI.

* "setup.py" - used to configure local paths.
* "text_extraction.py" - Python functions for text extraction (handling different file formats).
* "collect_and_preprocess.py" - Python functions for mainly executing document preprocessing steps.
* "utils.py" - support functions.
* "invoice_processing" - several things. It reads and preprocesses a product catalog; iterates through each PDF file in the specified directory; processes each file as an invoice (class instance); performs various calculations; identifies discrepancies between calculated subtotals and the sum of product prices, flags these invoices, and then compiles the data from all processed invoices into a single DataFrame. This DataFrame is then saved to a CSV file.
* "customers.py" - code used for masking client names, in order to preserve their identities.
* "post_processing.py" - extra steps for preparing data for deployment.
* "all.sql" - blocks of SQL code for creating, viewing and dropping tables from our database.
* "insert_into_db.py" - pipeline written in Python language for deploying data into our database.
* "dax_queries.txt" - blocks of DAX queries for creating customized measures in PowerBI.
* "reorder_suggestion.py" - code for generating a list of reorder suggestions for each client based on specific criteria.

Authors: Felipe Kalinoski Ferreira and Hassan Bhatti - Data Engineering students.
Project supervisor: Dr. Nina Rizun.
Interfaculty field of study: Data Engineering.
Realized at: Wydział Zarządzania i Ekonomii, Wydział Elektroniki, Telekomunikacji i Informatyki.
Profile: Data exploration in management.
