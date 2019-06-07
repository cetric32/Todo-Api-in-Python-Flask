from flask import Flask, request, jsonify
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
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    #check if user exists
    user = User.query.filter_by(name=data['name']).first()
    if user:
        return jsonify({'message': "User already exists,Try another name!"})
    new_user = User(name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': "New User Created!"})


@app.route('/user/<int:user_id>', methods=['PUT'])
def promote_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message': "No user found"})

    user.admin = True
    db.session.commit()
    return jsonify({'message': 'User has been promoted'})


@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'message': "No user found"})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'The user has been deleted'})





if __name__ == '__main__':
    app.run(debug=True, port=8080)