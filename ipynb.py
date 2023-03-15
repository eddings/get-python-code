import nbformat
import os
import ibm_db

# Set up the IBM DB2 connection
conn = ibm_db.connect("DATABASE=<database_name>;HOSTNAME=<hostname>;PORT=<port_number>;PROTOCOL=TCPIP;UID=<user_id>;PWD=<password>;", "", "")

# Define a function to extract the code cells from a notebook and save them to the database
def process_notebook(notebook_path):
    # Load the notebook from the .ipynb file
    with open(notebook_path, 'r') as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)

    # Extract the Python code cells
    code_cells = [cell for cell in nb.cells if cell.cell_type == 'code']
    for cell in code_cells:
        # Save the code cell to the database
        code = cell.source
        metadata = nb.metadata
        # Example SQL query to save the data to a table
        sql = "INSERT INTO notebooks (code, metadata) VALUES ('{}', '{}')".format(code, metadata)
        ibm_db.exec_immediate(conn, sql)

# Process all the notebooks in the download folder
download_folder = '/path/to/download/folder'
for filename in os.listdir(download_folder):
    if filename.endswith('.ipynb'):
        process_notebook(os.path.join(download_folder, filename))

# Close the IBM DB2 connection
ibm_db.close(conn)
