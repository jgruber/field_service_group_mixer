import os
from flask import Flask, send_file, request, abort

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'congregation.db')


@app.route('/')
def index():
    return send_file('index.html')


@app.route('/data/congregation.db', methods=['GET'])
def get_db():
    if os.path.exists(DB_PATH):
        return send_file(DB_PATH, mimetype='application/octet-stream')
    abort(404)


@app.route('/data/congregation.db', methods=['PUT'])
def put_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, 'wb') as f:
        f.write(request.get_data())
    return '', 204


@app.route('/data/congregation.db', methods=['DELETE'])
def delete_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        return '', 204
    abort(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
