import requests
import ibm_db

# Set up database connection
conn = ibm_db.connect("<your_db_name>", "<your_db_user>", "<your_db_password>")
repo_insert_stmt = ibm_db.prepare(conn, "INSERT INTO repositories (name, url, stars) VALUES (?, ?, ?)")
file_insert_stmt = ibm_db.prepare(conn, "INSERT INTO files (name, path, content, repository_id) VALUES (?, ?, ?, ?)")
select_stmt = ibm_db.prepare(conn, "SELECT id FROM repositories WHERE name = ?")

# Get list of all Python repositories on GitLab sorted by stars
url = "https://gitlab.com/api/v4/projects?search=python&order_by=stars&per_page=100"
headers = {'Private-Token': '<your_access_token>'}
response = requests.get(url, headers=headers)
repos = response.json()
python_repos = [repo for repo in repos if repo["name"].endswith(".py")]

# Save results to database
for repo in python_repos:
    name = repo["name"]
    url = repo["web_url"]
    stars = repo["star_count"]
    ibm_db.execute(repo_insert_stmt, (name, url, stars))
    ibm_db.execute(select_stmt, (name,))
    row = ibm_db.fetch_tuple(select_stmt)
    if row:
        repo_id = row[0]
        files_url = f"{url}/repository/tree?per_page=100"
        response = requests.get(files_url, headers=headers)
        files = response.json()
        for file in files:
            if file["type"] == "blob" and file["name"].endswith(".py"):
                content_url = f"{url}/repository/files/{file['path']}/raw?ref=master"
                response = requests.get(content_url, headers=headers)
                content = response.content.decode("utf-8")
                ibm_db.execute(file_insert_stmt, (file["name"], file["path"], content, repo_id))

# Close database connection
ibm_db.close(conn)
