import requests
import ibm_db

# Set up database connection
conn = ibm_db.connect("<your_db_name>", "<your_db_user>", "<your_db_password>")
solution_insert_stmt = ibm_db.prepare(conn, "INSERT INTO solutions (question_id, title, url, acceptance_rate) VALUES (?, ?, ?, ?)")
snippet_insert_stmt = ibm_db.prepare(conn, "INSERT INTO snippets (code, solution_id) VALUES (?, ?)")
select_stmt = ibm_db.prepare(conn, "SELECT id FROM solutions WHERE title = ?")

# Get list of all Python solutions on LeetCode sorted by acceptance rate
url = "https://leetcode.com/api/problems/all/"
response = requests.get(url)
problems = response.json()["stat_status_pairs"]
python_problems = [problem for problem in problems if problem["status"] == "ac" and problem["difficulty"]["level"] != 0 and problem["lang"] == "python3"]
python_problems_sorted = sorted(python_problems, key=lambda x: x["ac_rate"], reverse=True)

# Save results to database
for problem in python_problems_sorted:
    title = problem["stat"]["question__title"]
    url = f"https://leetcode.com/problems/{problem['stat']['question__title_slug']}/"
    acceptance_rate = problem["ac_rate"]
    ibm_db.execute(solution_insert_stmt, (problem["stat"]["question_id"], title, url, acceptance_rate))
    ibm_db.execute(select_stmt, (title,))
    row = ibm_db.fetch_tuple(select_stmt)
    if row:
        solution_id = row[0]
        code_url = f'https://leetcode.com/submissions/detail/{problem["id"]}/'
        response = requests.get(code_url)
        snippets = response.json()["code"]
        for snippet in snippets:
            code = snippet["text"]
            ibm_db.execute(snippet_insert_stmt, (code, solution_id))

# Close database connection
ibm_db.close(conn)
