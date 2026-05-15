import requests

url = "https://api.github.com/users/rong9835/repos"

resp = requests.get(url)
repos = resp.json()

# print(data)
data = []

for repo in repos:
    name = repo["name"]
    html_url = repo["html_url"]
    description = repo["description"]
    data.append({"name": name, "html_url": html_url, "desc": description})

print(f"{'리포이름':<30} {'리포URL':<50} 설명: {'설명':<20}")
for d in data:
    print(f"{d['name']:<30} {d['html_url']:<50}")
