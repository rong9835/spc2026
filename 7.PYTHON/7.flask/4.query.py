from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('q')
    page = request.args.get('page', default=1, type=int)

    user_input = f"Your query is {query} and page={page}"

    return jsonify({"message":user_input})

@app.route('/user/<username>/post')
def show_user_posts(username):
    page = request.args.get('page', default=1, type=int)
    result = f'User is {username} and page is {page}'
    return jsonify({"message": result})

if __name__ == '__main__':
    app.run(debug=True)
