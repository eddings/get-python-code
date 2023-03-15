import requests
import ibm_db

# Set up database connection
conn = ibm_db.connect("<your_db_name>", "<your_db_user>", "<your_db_password>")
repo_insert_stmt = ibm_db.prepare(conn, "INSERT INTO repositories (name, url, stars) VALUES (?, ?, ?)")
file_insert_stmt = ibm_db.prepare(conn, "INSERT INTO files (name, content, repository_id) VALUES (?, ?, ?)")
select_stmt = ibm_db.prepare(conn, "SELECT id FROM repositories WHERE name = ?")

# Get list of all Python repositories on GitHub sorted by stars
url = "https://api.github.com/search/repositories?q=language:python&sort=stars"
response = requests.get(url)
repos = response.json()["items"]

# Save results to database
for repo in repos:
    repo_name = repo["name"]
    url = repo["html_url"]
    stars = repo["stargazers_count"]
    ibm_db.execute(repo_insert_stmt, (repo_name, url, stars))
    ibm_db.execute(select_stmt, (repo_name,))
    row = ibm_db.fetch_tuple(select_stmt)
    if row:
        repository_id = row[0]
        code_url = f'https://api.github.com/repos/{repo["full_name"]}/contents/'
        response = requests.get(code_url)
        files = response.json()
        for file in files:
            if file["type"] == "file" and file["name"].endswith(".py"):
                file_name = file["name"]
                file_url = file["download_url"]
                file_content = requests.get(file_url).text
                ibm_db.execute(file_insert_stmt, (file_name, file_content, repository_id))

# Close database connection
ibm_db.close(conn)
