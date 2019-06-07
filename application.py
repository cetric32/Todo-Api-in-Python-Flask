from flask import Flask, request, jsonify, make_response, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///todo.db'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    admin = db.Column(db.Boolean)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)


@app.route('/user/', methods=['GET'])
def get_all_users():
    # check if user is logged in
    if 'name' not in session:
        return jsonify({'message': 'You need to login!'})
    # check if user is admin
    user = User.query.filter_by(name=session['name']).first()
    if not user.admin:
        return jsonify({'message': 'Cannot Perform that function'})
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)
    return jsonify({'users': output})


@app.route('/user/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    # check if user is logged in
    if 'name' not in session:
        return jsonify({'message': 'You need to login!'})
    # check if user is admin
    user = User.query.filter_by(name=session['name']).first()
    if not user.admin:
        return jsonify({'message': 'Cannot Perform that function'})
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message': "No user found"})

    user_data = {}
    user_data['id'] = user.id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    return jsonify({'user': user_data})


@app.route('/user/', methods=['POST'])
def create_user():
    # check if user is logged in
    if 'name' not in session:
        return jsonify({'message': 'You need to login!'})
    # check if user is admin
    user = User.query.filter_by(name=session['name']).first()
    if not user.admin:
        return jsonify({'message': 'Cannot Perform that function'})
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    # check if user exists
    user = User.query.filter_by(name=data['name']).first()
    if user:
        return jsonify({'message': "User already exists,Try another name!"})
    new_user = User(name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': "New User Created!"})


@app.route('/user/<int:user_id>', methods=['PUT'])
def promote_user(user_id):
    # check if user is logged in
    if 'name' not in session:
        return jsonify({'message': 'You need to login!'})
    # check if user is admin
    user = User.query.filter_by(name=session['name']).first()
    if not user.admin:
        return jsonify({'message': 'Cannot Perform that function'})
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message': "No user found"})

    user.admin = True
    db.session.commit()
    return jsonify({'message': 'User has been promoted'})


@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # check if user is logged in
    if 'name' not in session:
        return jsonify({'message': 'You need to login!'})
    # check if user is admin
    user = User.query.filter_by(name=session['name']).first()
    if not user.admin:
        return jsonify({'message': 'Cannot Perform that function'})
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message': "No user found"})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'The user has been deleted'})

# logging in functionality
@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    if check_password_hash(user.password, auth.password):
        session['name'] = auth.username
        return jsonify({'message': 'login successful!'})
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


# logging out functionality
@app.route('/logout')
def logout():
    # remove name from session if it is there
    session.pop('name', None)
    return jsonify({'message': 'Logout successful!'})


# defining the todo routes


@app.route('/todo', methods=['GET'])
def get_all_todos():
    # check if user is logged in
    if 'name' not in session:
        return jsonify({'message': 'You need to login!'})
    user = User.query.filter_by(name=session['name']).first()
    todos = Todo.query.filter_by(user_id=user.id).all()
    output = []

    for todo in todos:
        todo_data = {}
        todo_data['id'] = todo.id
        todo_data['text'] = todo.text
        todo_data['complete'] = todo.complete
        output.append(todo_data)
    return jsonify({'todos': output})

@app.route('/todo/<int:todo_id>', methods=['GET'])
def get_one_todo(todo_id):
    # check if user is logged in
    if 'name' not in session:
        return jsonify({'message': 'You need to login!'})
    user = User.query.filter_by(name=session['name']).first()
    todo = Todo.query.filter_by(id=todo_id, user_id=user.id).first()
    if not todo:
        return jsonify({'message': 'No todo Found!'})

    todo_data = {}
    todo_data['id'] = todo.id
    todo_data['text'] = todo.text
    todo_data['complete'] = todo.complete
    return jsonify({'todo': todo_data})


@app.route('/todo', methods=['POST'])
def create_todo():
    # check if user is logged in
    if 'name' not in session:
        return jsonify({'message': 'You need to login!'})
    user = User.query.filter_by(name=session['name']).first()
    data = request.get_json()

    new_todo = Todo(text=data['text'], complete=False, user_id=user.id)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({'message': 'New Todo Created!'})


@app.route('/todo/<int:todo_id>', methods=['PUT'])
def complete_todo(todo_id):
    # check if user is logged in
    if 'name' not in session:
        return jsonify({'message': 'You need to login!'})
    user = User.query.filter_by(name=session['name']).first()
    todo = Todo.query.filter_by(id=todo_id, user_id=user.id).first()
    if not todo:
        return jsonify({'message': 'No todo Found!'})
    todo.complete = True
    db.session.commit()
    return jsonify({'message': "Todo Item has been completed"})


@app.route('/todo/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    # check if user is logged in
    if 'name' not in session:
        return jsonify({'message': 'You need to login!'})
    user = User.query.filter_by(name=session['name']).first()
    todo = Todo.query.filter_by(id=todo_id, user_id=user.id).first()
    if not todo:
        return jsonify({'message': 'No todo Found!'})
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'Todo Item has been deleted!'})


if __name__ == '__main__':
    app.run(debug=True, port=8080)
