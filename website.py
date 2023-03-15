import re
import ibm_db
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

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
python_pattern = re.compile(r"<pre class=\"brush: python;\">(.*?)</pre>", re.DOTALL)

# Define function to extract Python code from URL and save to database
def extract_python_code(url):
    try:
        # Make HTTP request and parse HTML
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract Python code from HTML using regular expressions
        python_matches = soup.find_all("pre", {"class": "brush: python;"})
        python_code = []
        for match in python_matches:
            python_code.extend(python_pattern.findall(str(match)))

        # Save details to DB2 database
        for code in python_code:
            ibm_db.exec_immediate(conn, f"INSERT INTO PYTHON_CODE (URL, CODE) VALUES ('{url}', '{code}')")
    except Exception as e:
        print(f"Error extracting data from {url}: {e}")

    # Recursively follow links within domain
    for link in soup.find_all("a", href=True):
        link_url = urljoin(url, link["href"])
        parsed_url = urlparse(link_url)
        if parsed_url.netloc == domain and parsed_url.scheme == "https":
            extract_python_code(link_url)

# Define domain to scrape
domain = "example.com"

# Start scraping from homepage of domain
homepage_url = f"https://{domain}"
extract_python_code(homepage_url)

# Disconnect from DB2 database
ibm_db.close(conn)
