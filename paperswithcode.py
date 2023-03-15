import requests
from bs4 import BeautifulSoup
import ibm_db_dbi as dbi

# Set up database connection
dsn_driver = "IBM DB2 ODBC DRIVER"
dsn_database = "<your_db_name>"
dsn_hostname = "<your_db_hostname>"
dsn_port = "<your_db_port>"
dsn_uid = "<your_db_username>"
dsn_pwd = "<your_db_password>"
dsn_protocol = "TCPIP"
dsn_security = "SSL"

dsn = (
    "DRIVER={0};DATABASE={1};HOSTNAME={2};PORT={3};PROTOCOL={4};UID={5};PWD={6};Security={7};"
    .format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd, dsn_security)
)
conn = dbi.connect(dsn)

insert_paper_stmt = conn.cursor().execute("INSERT INTO papers (title, url, stars, date, conference) VALUES (?, ?, ?, ?, ?)")
insert_code_stmt = conn.cursor().execute("INSERT INTO papers_code_files (paper_id, filename, content) VALUES (?, ?, ?)")

# Get list of all papers tagged with "Python" on Papers with Code
url = "https://paperswithcode.com/search?q=python"
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')
papers = soup.find_all("div", class_="col-lg-9 col-md-8 col-sm-12")

# Save results to database
for paper in papers:
    title = paper.find("h2", class_="paper-title").text.strip()
    url = "https://paperswithcode.com" + paper.find("a")["href"]
    stars = int(paper.find("div", class_="star-wraper").text.strip())
    date = paper.find("p", class_="published-date").text.strip()
    conference = paper.find("span", class_="conference-info").text.strip()
    insert_paper_stmt.execute((title, url, stars, date, conference))

    # Get associated code files for each paper
    code_url = url + "/code"
    code_page = requests.get(code_url)
    code_soup = BeautifulSoup(code_page.content, 'html.parser')
    code_files = code_soup.find_all("div", class_="code-file")

    # Save each code file to database
    paper_id = conn.cursor().lastrowid
    for code_file in code_files:
        filename = code_file.find("div", class_="file-name").text.strip()
        content = code_file.find("pre", class_="code").text.strip()
        insert_code_stmt.execute((paper_id, filename, content))

# Commit changes and close database connection
conn.commit()
conn.close()
