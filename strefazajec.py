from bs4 import BeautifulSoup
import requests

# Fetch the HTML
url = 'https://www.strefazajec.pl/course/view/id/65821'
response = requests.get(url)

# Parse the HTML
soup = BeautifulSoup(response.text, 'html.parser')

title = soup.select_one("h1[class!=logo]")
print(title.text)

# Define CSS
# for lesson in soup.find_all("tr", {"class":"lesson_record"}):
#     for td in lesson.find_all("td"):
#         print(td.text.strip())