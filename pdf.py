import os
import re
import ibm_db
from io import StringIO
from pdfminer.high_level import extract_text_to_fp

# Connect to DB2 database
dsn_driver = "{IBM DB2 ODBC DRIVER}"
dsn_database = "DATABASE_NAME"
dsn_hostname = "HOSTNAME"
dsn_port = "PORT"
dsn_protocol = "TCPIP"
dsn_uid = "USERNAME"
dsn_pwd = "PASSWORD"
dsn = (
    f"DRIVER={dsn_driver};"
    f"DATABASE={dsn_database};"
    f"HOSTNAME={dsn_hostname};"
    f"PORT={dsn_port};"
    f"PROTOCOL={dsn_protocol};"
    f"UID={dsn_uid};"
    f"PWD={dsn_pwd};"
)
conn = ibm_db.connect(dsn, "", "")

# Define regular expression pattern to match Python code
python_pattern = re.compile(r"```python(.*?)```", re.DOTALL)

# Extract Python code from PDF files and save to DB2 database
directory = "/path/to/directory/with/pdfs"
for filename in os.listdir(directory):
    if filename.endswith(".pdf"):
        filepath = os.path.join(directory, filename)
        with open(filepath, "rb") as fp:
            # Extract text from PDF file
            text = StringIO()
            extract_text_to_fp(fp, text)
            text = text.getvalue()

            # Extract Python code using regular expressions
            python_matches = python_pattern.findall(text)

            # Save Python code to DB2 database
            for match in python_matches:
                try:
                    ibm_db.exec_immediate(conn, f"INSERT INTO PYTHON_CODE (CODE) VALUES ('{match}')")
                except Exception as e:
                    print(f"Error inserting data for file {filename}: {e}")

# Disconnect from DB2 database
ibm_db.close(conn)
