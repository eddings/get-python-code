import requests
import ibm_db

# Set up database connection
conn = ibm_db.connect("<your_db_name>", "<your_db_user>", "<your_db_password>")
gist_insert_stmt = ibm_db.prepare(conn, "INSERT INTO gists (url, description, stars) VALUES (?, ?, ?)")
file_insert_stmt = ibm_db.prepare(conn, "INSERT INTO files (name, content, gist_id) VALUES (?, ?, ?)")
select_stmt = ibm_db.prepare(conn, "SELECT id FROM gists WHERE url = ?")

# Get list of all public Gists containing Python code on GitHub
url = "https://api.github.com/gists/public"
params = {'per_page': 100}
headers = {'Authorization': 'token <your_access_token>'}
gists = []
while True:
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        break
    result = response.json()
    if not result:
        break
    gists.extend(result)
    if 'next' not in response.links:
        break
    url = response.links['next']['url']

python_gists = [gist for gist in gists if any(file["language"] == "Python" for file in gist["files"].values())]

# Save results to database
for gist in python_gists:
    url = gist["html_url"]
    description = gist["description"]
    stars = gist["stargazers_count"]
    ibm_db.execute(gist_insert_stmt, (url, description, stars))
    ibm_db.execute(select_stmt, (url,))
    row = ibm_db.fetch_tuple(select_stmt)
    if row:
        gist_id = row[0]
        for file in gist["files"].values():
            if file["language"] == "Python":
                content_url = file["raw_url"]
                response = requests.get(content_url, headers=headers)
                content = response.content.decode("utf-8")
                ibm_db.execute(file_insert_stmt, (file["filename"], content, gist_id))

# Close database connection
ibm_db.close(conn)
