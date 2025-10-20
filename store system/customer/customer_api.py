from flask import Flask, jsonify, request
import os
from jwtauth import JWTAuth
from orm import db, Product, Category, Order, OrderProduct, OrderStatus, ProductCategory
from customer_database_service import CustomerDatabaseService
from blockchain import GanacheClient

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
customerDatabaseService = CustomerDatabaseService(db, Product, Category, Order, OrderProduct, OrderStatus, ProductCategory)
# create service for interacting with the blockchain
ganacheClient = GanacheClient()

# function for JWT authentication
def auth(role):
    token = request.headers.get('Authorization')
    if not token:
        return "", "", 401

    email, r = JWTAuth.validate_token(token.replace('Bearer ', ''))
    if not email or not r or r != role:
        return "", "", 401

    return email, role, 200

# endpoint receives product name and category name
# endpoint returns list of categories which names contain given category name
# and a list of products which names contain given product name
@app.route('/search', methods=['GET'])
def search():
    email, role, status = auth('customer')
    if status != 200:
        return jsonify({'msg': "Missing Authorization Header"}), status

    # get names from the request body
    name = request.args.get('name')
    category = request.args.get('category')

    response = customerDatabaseService.search_for_products(name, category)
    return jsonify(response), 200

# function that check list of products for missing or invalid ids, missing or invalid quantities
# and products that exist in the database
def check_order_request(products):
    for index, product in enumerate(products):
        if 'id' not in product:
            return f"Product id is missing for request number {index}.", 400
    for index, product in enumerate(products):
        if 'quantity' not in product:
            return f"Product quantity is missing for request number {index}.", 400
    for index, product in enumerate(products):
        try:
            id = int(product['id'])
            if id <= 0:
                return f"Invalid product id for request number {index}.", 400
        except Exception:
            return f"Invalid product id for request number {index}.", 400
    for index, product in enumerate(products):
        try:
            quantity = int(product['quantity'])
            if quantity <= 0:
                return f"Invalid product quantity for request number {index}.", 400
        except Exception:
            return f"Invalid product quantity for request number {index}.", 400

    message, status = customerDatabaseService.check_products(products)
    return message, status

# endpoint receives product ids and quantities and makes order with them
@app.route('/order', methods=['POST'])
def order():
    email, role, status = auth('customer')
    if status != 200:
        return jsonify({'msg': "Missing Authorization Header"}), status

    # check for if request body is missing any information
    data = request.get_json()
    if not 'requests' in data:
        return jsonify({'message': "Field requests is missing."}), 400

    products = data['requests']
    message, status = check_order_request(products)
    if status != 200:
        return jsonify({'message': message}), status

    if not 'address' in data:
        return jsonify({'message': "Field address is missing."}), 400

    address = data['address']
    if address == '':
        return jsonify({'message': "Field address is missing."}), 400

    # check if given account address if valid and has enough meanss
    if not ganacheClient.check_address(address):
        return jsonify({'message': "Invalid address."}), 400

    # submit order to the databases
    message, status = customerDatabaseService.make_order(products, email)
    if status != 200:
        return jsonify({'message': message}), status

    order_id = int(message)

    # calculate total price
    total_price = customerDatabaseService.get_total_price(order_id)
    # create and deploy smart contract with customers address and total price of the order
    contract_address = ganacheClient.deploy_contract(address, total_price)
    # set contract address in order
    customerDatabaseService.set_address(order_id, contract_address)

    return jsonify({'id': order_id}), 200

# endpoint returns all orders of a customer based on his email
@app.route('/status', methods=['GET'])
def status():
    email, role, status = auth('customer')
    if status != 200:
        return jsonify({'msg': "Missing Authorization Header"}), status

    result = customerDatabaseService.get_orders(email)
    return jsonify(result), 200

# endpoint marks order as delivered in the database and in the smart contract
@app.route('/delivered', methods=['POST'])
def delivered():
    email, role, status = auth('customer')
    if status != 200:
        return jsonify({'msg': "Missing Authorization Header"}), status

    # check for any missing field in the request body
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"message": "Missing order id."}), 400

    order_id = data['id']
    try:
        order_id = int(order_id)
        if order_id < 0:
            return jsonify({"message": "Invalid order id."}), 400
    except (ValueError, TypeError):
        return jsonify({"message": "Invalid order id."}), 400

    # check if order exists in the databases
    message, status = customerDatabaseService.check_order(order_id)
    if status != 200:
        return jsonify({'message': message}), status

    # confirm delivery in the database
    message, status = customerDatabaseService.confirm_delivery(order_id)
    if status != 200:
        return jsonify({'message': message}), status

    # confirm delivery in the smart contract
    contract_address, _ = customerDatabaseService.get_address(order_id)
    ganacheClient.confirm_delivery(contract_address)

    return jsonify({"message": message}), status

# endpoint returns transaction that customer has to pays
@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    email, role, status = auth('customer')
    if status != 200:
        return jsonify({'msg': "Missing Authorization Header"}), status

    # check for any missing fields in the request body
    data = request.get_json()
    if not 'id' in data:
        return jsonify({"message": "Missing order id."}), 400
    try:
        id = int(data['id'])
        if id <= 0:
            return jsonify({"message": "Invalid order id."}), 400
    except Exception:
        return jsonify({"message": "Invalid order id."}), 400

    # check if order exists in the database
    order_id = int(id)
    message, status = customerDatabaseService.check_order(order_id)
    if status != 200:
        return jsonify({'message': message}), status

    if 'address' not in data:
        return jsonify({"message": "Missing address."}), 400

    # check if customer's account address is valid
    address = data['address']
    if not ganacheClient.check_address(address):
        return jsonify({'message': "Invalid address."}), 400

    # get contract address
    contract_address, status = customerDatabaseService.get_address(order_id)
    # generate invoice
    status, message = ganacheClient.generate_invoice(contract_address, address)
    if not status:
        return jsonify({'message': message}), 400

    return jsonify({'invoice': message}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5002)