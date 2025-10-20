from flask import Flask, jsonify, request
from user_database_service import UserDatabaseService
from orm import db, User
import os
from jwtauth import JWTAuth

host = os.getenv("DB_HOST", "localhost")
port = int(os.getenv("DB_PORT", 3306))
user = os.getenv("DB_USER", "")
password = os.getenv("DB_PASSWORD", "")
database = os.getenv("DB_NAME", "")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

userDatabaseService = UserDatabaseService(db, User)

@app.route('/register_customer', methods=['POST'])
def register_customer():
    message, status = userDatabaseService.insert_user(request.json, 'customer')
    return jsonify({"message": message}), status

@app.route('/register_courier', methods=['POST'])
def register_courier():
    message, status = userDatabaseService.insert_user(request.json, 'courier')
    return jsonify({"message": message}), status

@app.route('/login', methods=['POST'])
def login():
    message, status = userDatabaseService.check_user(request.json)
    if status != 200:
        return jsonify({"message": message}), status

    token = JWTAuth.generate_token(data={"email": message.email, "password": message.password, "forename": message.forename, "surname": message.surname, "role": message.role.name})
    return jsonify({"accessToken": token}), status

@app.route('/delete', methods=['POST'])
def delete():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"msg": "Missing Authorization Header"}), 401
    token = token.replace('Bearer ', '')

    email = JWTAuth.validate_token(token)
    if email is None:
        return jsonify({"msg": "Missing Authorization Header"}), 401

    message, status = userDatabaseService.delete_user({"email": email})
    return jsonify({"message": message}), status

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0" ,port=5000)