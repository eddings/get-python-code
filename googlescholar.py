import scholarly
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Set up PDF canvas
pdf_file = "python_code.pdf"
c = canvas.Canvas(pdf_file, pagesize=letter)
text = c.beginText()
text.setTextOrigin(50, 700)

# Search for papers with the keyword "Python"
search_query = scholarly.search_keyword("Python")

# Get code from GitHub and save to PDF
for i, paper in enumerate(search_query):
    url = paper.bib.get("url")
    if "github" in url:
        # Extract repository name from URL
        repo_name = url.split("/")[-2] + "/" + url.split("/")[-1]

        # Get repository data from GitHub API
        repo_data = requests.get(f"https://api.github.com/repos/{repo_name}").json()

        # Get repository contents from GitHub API
        repo_contents = requests.get(f"https://api.github.com/repos/{repo_name}/contents").json()

        # Save repository code to PDF
        text.textLine(f"Repository: {repo_name}")
        for content in repo_contents:
            if content.get("type") == "file" and content.get("name").endswith(".py"):
                file_url = content.get("download_url")
                file_code = requests.get(file_url).text
                text.textLine(f"\n\nFile: {content.get('name')}\n\n")
                text.textLines(file_code)
    
    # Limit number of papers saved to 10 for example purposes
    if i >= 9:
        break

# Add text to PDF and save
c.drawText(text)
c.showPage()
c.save()

print(f"Python code saved to {pdf_file}")
