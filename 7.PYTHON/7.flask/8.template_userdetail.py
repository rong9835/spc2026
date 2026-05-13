from flask import Flask, render_template

app = Flask(__name__)

users = [
    {'name': '홍길동', 'age': 25, 'phone': '123-456-7890'},
    {'name': '고길동', 'age': 30, 'phone': '123-555-7890'},
    {'name': '김길동', 'age': 27, 'phone': '321-777-7890'},
    {'name': '이길동', 'age': 25, 'phone': '321-888-7890'},
]

@app.route('/')
def index():
    final_html = render_template('users_detail.html', users=users)
    print(final_html)
    return final_html

if __name__ == '__main__':
    app.run(debug=True)
