import os
import json
from functools import wraps
from flask import Flask, send_file, request, abort, Response, jsonify

app = Flask(__name__)

DATA_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DB_PATH    = os.path.join(DATA_DIR, 'congregation.db')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# ─── User store ────────────────────────────────────────────────────────────

def load_users():
    if not os.path.exists(USERS_FILE):
        os.makedirs(DATA_DIR, exist_ok=True)
        users = {'admin': 'changeme'}
        _save_users(users)
        return users
    with open(USERS_FILE) as f:
        return json.load(f)

def _save_users(users):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# ─── Auth ──────────────────────────────────────────────────────────────────

def _check_auth(username, password):
    users = load_users()
    return users.get(username) == password

def _auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not _check_auth(auth.username, auth.password):
            return Response(
                'Authentication required.',
                401,
                {'WWW-Authenticate': 'Basic realm="Field Service Group Mixer"'}
            )
        return f(*args, **kwargs)
    return decorated

# ─── App routes ────────────────────────────────────────────────────────────

@app.route('/')
@_auth_required
def index():
    return send_file('index.html')

@app.route('/favicon.svg')
def favicon():
    return send_file('favicon.svg', mimetype='image/svg+xml')

@app.route('/data/congregation.db', methods=['GET'])
@_auth_required
def get_db():
    if os.path.exists(DB_PATH):
        return send_file(DB_PATH, mimetype='application/octet-stream')
    abort(404)

@app.route('/data/congregation.db', methods=['PUT'])
@_auth_required
def put_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DB_PATH, 'wb') as f:
        f.write(request.get_data())
    return '', 204

@app.route('/data/congregation.db', methods=['DELETE'])
@_auth_required
def delete_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        return '', 204
    abort(404)

# ─── User management ───────────────────────────────────────────────────────

@app.route('/api/users', methods=['GET'])
@_auth_required
def list_users():
    return jsonify(list(load_users().keys()))

@app.route('/api/users', methods=['POST'])
@_auth_required
def add_user():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400
    users = load_users()
    if username in users:
        return jsonify({'error': f'User "{username}" already exists.'}), 409
    users[username] = password
    _save_users(users)
    return jsonify({'message': 'User created.'}), 201

@app.route('/api/users/<username>/password', methods=['PUT'])
@_auth_required
def change_password(username):
    data = request.get_json(silent=True) or {}
    password = data.get('password', '')
    if not password:
        return jsonify({'error': 'Password is required.'}), 400
    users = load_users()
    if username not in users:
        return jsonify({'error': 'User not found.'}), 404
    users[username] = password
    _save_users(users)
    return jsonify({'message': 'Password updated.'})

@app.route('/api/users/<username>', methods=['DELETE'])
@_auth_required
def delete_user(username):
    users = load_users()
    if username not in users:
        return jsonify({'error': 'User not found.'}), 404
    if len(users) <= 1:
        return jsonify({'error': 'Cannot delete the last remaining user.'}), 400
    del users[username]
    _save_users(users)
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
