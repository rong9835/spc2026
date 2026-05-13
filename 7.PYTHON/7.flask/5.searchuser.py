from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

users = [
    {'name': 'Alice', 'age': 25, 'phone': '123-456-7890'},
    {'name': 'Bob', 'age': 30, 'phone': '123-555-7890'},
    {'name': 'Charlie', 'age': 27, 'phone': '321-777-7890'},
    {'name': 'David', 'age': 25, 'phone': '321-888-7890'},
]

@app.route('/search')
def search_user():
    name = request.args.get('name')
    age = request.args.get('age')
    phone = request.args.get('phone')

    result = users

    # 쿼리 파라미터로 name, age, phone 로 검색해서 결과를 반환한다.
    if name:
        result = [u    for u in result    if name.lower() in u['name'].lower()]

    if age:
        result = [u    for u in result    if int(age) == u['age']]

    # 기능 추가 - 국번으로 조회하기 (앞글자 startswith 로...)
    if phone:
        # result = [u    for u in result    if phone == u['phone']]
        result = [u    for u in result    if u['phone'].startswith(phone)]

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
