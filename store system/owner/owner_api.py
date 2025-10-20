from flask import Flask, jsonify, request
import os
from jwtauth import JWTAuth
from orm import db, Product, Category, Order, OrderProduct, OrderStatus, ProductCategory
from owner_database_service import OwnerDatabaseService
import csv
import io

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
storeDatabaseService = OwnerDatabaseService(db, Product, Category, Order, OrderProduct, OrderStatus, ProductCategory)

# function for JWT authentication
def auth(role):
    token = request.headers.get('Authorization')
    if not token:
        return "", "", 401

    email, r = JWTAuth.validate_token(token.replace('Bearer ', ''))
    if not email or not r or r != role:
        return "", "", 401

    return email, role, 200

# function that parses given CSV file, format product data and return it
def parse_csv(file):
    # open given file
    stream = io.StringIO(file.stream.read().decode("utf-8"))
    csv_reader = csv.reader(stream)

    # parse it and format products
    products = []
    for index, row in enumerate(csv_reader):
        if len(row) != 3:
            return f"Incorrect number of values on line {index}.", 400

        categories = [c.strip() for c in row[0].split('|')]
        name = row[1].strip()
        price = row[2].strip()

        products.append((categories, name, price))

    return products, 200

# endpoint for adding products to the database
# product info is in CSV file that is sent
@app.route('/update', methods=['POST'])
def update():
    email, role, status = auth('owner')
    if status != 200:
        return jsonify({'msg': "Missing Authorization Header"}), status

    # check if file is missing in the request
    if 'file' not in request.files:
        return jsonify({'message': 'Field file is missing.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'Field file missing.'}), 400

    # parse the file
    products, status = parse_csv(file)
    if status != 200:
        return jsonify({"message": products}), status

    # add all products
    message, status = storeDatabaseService.add_products(products)

    return jsonify({"message": message}), status

# endpoint that returns statistics for products that have been sold at least once
@app.route('/product_statistics', methods=['GET'])
def product_statistics():
    email, role, status = auth('owner')
    if status != 200:
        return jsonify({'msg': "Missing Authorization Header"}), status

    stats = storeDatabaseService.product_stats()
    return jsonify({"statistics": stats}), 200

# endpoint that returns category names sorted by number of sold products and by name
@app.route('/category_statistics', methods=['GET'])
def category_statistics():
    email, role, status = auth('owner')
    if status != 200:
        return jsonify({'msg': "Missing Authorization Header"}), status

    stats = storeDatabaseService.category_stats()
    return jsonify({"statistics": stats}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)