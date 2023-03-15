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

# Define regular expression patterns to match Python code and metadata
python_pattern = re.compile(r"<pre class=\"brush: python;\">(.*?)</pre>", re.DOTALL)
title_pattern = re.compile(r"<title>(.*?)</title>")
description_pattern = re.compile(r'<meta name="description" content="(.*?)"')

# Define function to extract Python code and metadata from URL and save to database
def extract_data(url):
    try:
        # Make HTTP request and parse HTML
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract Python code from HTML using regular expressions
        python_matches = soup.find_all("pre", {"class": "brush: python;"})
        python_code = []
        for match in python_matches:
            python_code.extend(python_pattern.findall(str(match)))

        # Extract metadata from HTML using regular expressions
        title_match = title_pattern.search(response.text)
        title = title_match.group(1) if title_match else ""
        description_match = description_pattern.search(response.text)
        description = description_match.group(1) if description_match else ""

        # Save details to DB2 database
        for code in python_code:
            ibm_db.exec_immediate(conn, f"INSERT INTO WEBPAGE_DATA (URL, TITLE, DESCRIPTION, CODE) VALUES ('{url}', '{title}', '{description}', '{code}')")
    except Exception as e:
        print(f"Error extracting data from {url}: {e}")

    # Recursively follow links within domain
    for link in soup.find_all("a", href=True):
        link_url = urljoin(url, link["href"])
        parsed_url = urlparse(link_url)
        if parsed_url.netloc == domain and parsed_url.scheme == "https":
            extract_data(link_url)

# Define domain to scrape
domain = "example.com"

# Start scraping from homepage of domain
homepage_url = f"https://{domain}"
extract_data(homepage_url)

# Disconnect from DB2 database
ibm_db.close(conn)
