import requests

url = "https://www.example.com"

response = requests.get(url)

html = response.text

print(html)

print("-"*30)

#  원하는 태그 찾아오기
start = html.find("<h1>")
end = html.find("</h1>")

text = html[start+4:end]
print(text)
