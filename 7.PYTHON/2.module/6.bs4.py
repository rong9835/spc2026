# pip install bs4
from bs4 import BeautifulSoup

html = """
<html>
    <head>
        <title>Hello</title>
    </head>
    <body>
        <h1>Title</h1>
        <p>여기는 첫번째 파라그래프</p>
        <p>여기는 두번째 파라그래프</p>
    </body>
</html>
"""

soup = BeautifulSoup(html, "html.parser")

print(soup)

heading = soup.find_all('h1')
paragraph = soup.find_all('p')

print(heading)
print(paragraph)
