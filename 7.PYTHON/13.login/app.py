from flask import Flask, render_template, request

app = Flask(__name__)

# 사용자 로컬 DB
users = [
    {'name': '홍길동', 'id': 'hong', 'pw': '1234'},
    {'name': '고길동', 'id': 'gil', 'pw': 'abcd'},
    {'name': '김길동', 'id': 'dong', 'pw': 'qwe123'},
]

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']
        print(f"입력값: {id}, {pw}")

        user = None
        for u in users:
            if u['id'] == id and u['pw'] == pw:
                user = u

        if user:
            error = None
        else:
            error = "Invalid ID or PW"

        return render_template('index.html', user=user, error=error)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
