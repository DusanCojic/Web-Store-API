from flask import Flask, jsonify, request
import os

from blockchain import GanacheClient
from jwtauth import JWTAuth
from orm import db, Product, Category, Order, OrderProduct, OrderStatus, ProductCategory
from courier_database_service import CourierDatabaseService

# read the environment variables
host = os.getenv("DB_HOST", "localhost")
port = int(os.getenv("DB_PORT", 3306))
user = os.getenv("DB_USER", "")
password = os.getenv("DB_PASSWORD", "")
database = os.getenv("DB_NAME", "")

# initialize the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# initialize the database
db.init_app(app)

# create service for interacting with database
courierDatabaseService = CourierDatabaseService(db, Product, Category, Order, OrderProduct, OrderStatus, ProductCategory)
# create service for interacting with the blockchain
ganacheClient = GanacheClient()

# function for JWT authentication
def auth(role):
    # read the token from the header
    token = request.headers.get('Authorization')
    if not token:
        return "", "", 401

    # get email and role of the caller from the JWT
    email, r = JWTAuth.validate_token(token.replace('Bearer ', ''))
    if not email or not r or r != role:
        return "", "", 401

    return email, role, 200

# endpoint returns list of orders that are not taken by the courier
@app.route('/orders_to_deliver', methods=['GET'])
def orders_to_deliver():
    email, role, status = auth('courier')
    if status != 200:
        return jsonify({'msg': "Missing Authorization Header"}), status

    orders = courierDatabaseService.orders_to_deliver()
    return jsonify({"orders": orders}), 200

# endpoint receives id of the order that courier wants to pick up and his account address
# endpoint marks order as picked by the courier and binds his account address to the smart contract related to the given order
@app.route('/pick_up_order', methods=['POST'])
def pick_up_order():
    email, role, status = auth('courier')
    if status != 200:
        return jsonify({'msg': "Missing Authorization Header"}), status

    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"message": "Missing order id."}), 400

    # check for any error in the request (missing or invalid order id or address)
    order_id = data['id']
    message, status = courierDatabaseService.check_order(order_id)
    if status != 200:
        return jsonify({'message': message}), status

    if 'address' not in data:
        return jsonify({"message": "Missing address."}), 400

    address = data['address']
    if address == '':
        return jsonify({"message": "Missing address."}), 400

    if not ganacheClient.check_address(address):
        return jsonify({"message": "Invalid address."}), 400

    # check whether customer has paid
    contract_address = courierDatabaseService.get_address(order_id)
    owner, customer, courier, price, paid, delivered, courier_bound = ganacheClient.get_contract_status(contract_address)
    if not paid:
        return jsonify({"message": "Transfer not complete."}), 400

    # mark order as picked
    courierDatabaseService.pick_up_order(order_id)
    # bind courier to the smart contract
    _ = ganacheClient.assign_courier(contract_address, address)

    return jsonify({"message": ""}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5003)