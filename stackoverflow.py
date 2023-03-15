import requests
import ibm_db

# Set up database connection
conn = ibm_db.connect("<your_db_name>", "<your_db_user>", "<your_db_password>")
question_insert_stmt = ibm_db.prepare(conn, "INSERT INTO questions (title, url, votes) VALUES (?, ?, ?)")
snippet_insert_stmt = ibm_db.prepare(conn, "INSERT INTO snippets (code, question_id) VALUES (?, ?)")
select_stmt = ibm_db.prepare(conn, "SELECT id FROM questions WHERE title = ?")

# Get list of all Python questions on Stack Overflow sorted by votes
url = "https://api.stackexchange.com/2.3/questions?order=desc&sort=votes&tagged=python&site=stackoverflow"
response = requests.get(url)
questions = response.json()["items"]

# Save results to database
for question in questions:
    title = question["title"]
    url = question["link"]
    votes = question["score"]
    ibm_db.execute(question_insert_stmt, (title, url, votes))
    ibm_db.execute(select_stmt, (title,))
    row = ibm_db.fetch_tuple(select_stmt)
    if row:
        question_id = row[0]
        code_url = f'https://api.stackexchange.com/2.3/questions/{question["question_id"]}/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody'
        response = requests.get(code_url)
        snippets = response.json()["items"]
        for snippet in snippets:
            code = snippet["body"]
            ibm_db.execute(snippet_insert_stmt, (code, question_id))

# Close database connection
ibm_db.close(conn)
