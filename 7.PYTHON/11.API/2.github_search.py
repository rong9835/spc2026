import requests

url = 'https://api.github.com/search/repositories'

keyword = "chatbot"

params = {
    'q': keyword,
    'per_page': 100,
    'page': 2
}

resp = requests.get(url, params)
data = resp.json()

# print(data)
if 'items' in data:
    repos = data['items']
    for repo in repos:
        name = repo['name']
        full_name = repo['full_name']
        html_url = repo['html_url']
        desc = repo['description']

        print(f'리포명: {name}, 풀네임: {full_name}, URL: {html_url}, 설명: {desc}')
