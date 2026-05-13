from flask import Flask, jsonify

app = Flask(__name__)

users = [
    {'name': 'Alice', 'age': 25, 'phone': '123-456-7890'},
    {'name': 'Bob', 'age': 30, 'phone': '123-555-7890'},
    {'name': 'Charlie', 'age': 27, 'phone': '123-777-7890'},
    {'name': 'David', 'age': 25, 'phone': '123-888-7890'},
]
# 파이썬의 리스트 폼, 각각의 리스트에는 딕셔너리

@app.route('/')
def main():
    return jsonify(users)  # 우리의 백엔드 list/dict 구조를 웹이 좋아하는 JSON 포멧으로 변환해서 보내줌

@app.route('/user/<name>')
def get_user_by_name(name):
    print("사용자입력값: ", name)
    user = None

    for u in users:
        if u['name'].lower() == name.lower():
            user = u

    if user:
        return jsonify(user)
    else:
        return jsonify({"message": "User not found"})

@app.route('/user/<int:age>')
def get_user_by_age(age):
    print("사용자입력값: ", age)
    # 나이가 같은 두명을 다 반환하려면 어떻게 해야할까??
    user = []

    for u in users:
        if u['age'] == age:
            user.append(u)
            
    if user:
        return jsonify(user)
    else:
        return jsonify({"message": "User not found"})

if __name__ == '__main__':
    app.run(debug=True)
