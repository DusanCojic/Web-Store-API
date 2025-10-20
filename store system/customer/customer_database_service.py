from sqlalchemy import func

class CustomerDatabaseService:
    def __init__(self, db, Product, Category, Order, OrderProduct, OrderStatus, ProductCategory):
        self.db = db
        self.Product = Product
        self.Category = Category
        self.Order = Order
        self.OrderProduct = OrderProduct
        self.OrderStatus = OrderStatus
        self.ProductCategory = ProductCategory

    # function that returns list of categories which names contain text given by parameter category
    # and list of products which names contain text given by the parameter name and are in given category
    def search_for_products(self, name, category):
        if name == "" and category == "":
            return []

        # create queries for products
        product_query = self.Product.query
        if name:
            product_query = product_query.filter(self.Product.name.ilike(f"%{name}%"))
        if category:
            product_query = product_query.join(self.Product.categories).filter(self.Category.name.ilike(f"%{category}%"))

        # execute the query and parse the result
        products = product_query.distinct().all()
        products = [
            {
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "categories": [c.name for c in product.categories]
            }
            for product in products
        ]

        # create queries for categories
        category_query = self.Category.query
        if category:
            category_query = category_query.filter(self.Category.name.ilike(f"%{category}%"))

        if name:
            category_query = category_query.join(self.Category.products).filter(self.Product.name.ilike(f"%{name}%"))

        # execute query and parse the result
        categories = category_query.distinct().all()
        categories = [c.name for c in categories]

        # format final result
        response = {
            "categories": categories,
            "products": products
        }

        return response

    # function that check whether some of the products given does not exit in the database
    def check_products(self, products):
        for index, product in enumerate(products):
            product_record = self.Product.query.filter_by(id=product['id']).first()
            if not product_record:
                return f"Invalid product for request number {index}.", 400

        return "", 200

    # function that checks whether order exists in the database based on its id
    def check_order(self, order_id):
        order = self.Order.query.filter_by(id=order_id).first()
        if not order:
            return "Invalid order id.", 400
        return "", 200

    # function that creates order and inserts it in the database
    def make_order(self, products, email):
        order = self.Order(email=email, status=self.OrderStatus.CREATED, address="")

        for index, product in enumerate(products):
            product_record = self.Product.query.filter_by(id=product['id']).first()
            order_product = self.OrderProduct(product=product_record, quantity=float(product['quantity']))
            order.products.append(order_product)

        self.db.session.add(order)
        self.db.session.commit()

        return order.id, 200

    # function that sets smart contract address in the given order
    def set_address(self, order_id, address):
        order = self.Order.query.filter_by(id=order_id).first()
        order.address = address
        self.db.session.add(order)
        self.db.session.flush()
        self.db.session.commit()

    # function that returns smart contract address for the given order
    def get_address(self, order_id):
        order = self.Order.query.filter_by(id=order_id).first()
        if not order:
            return "Invalid order id.", 400
        return order.address, 200

    # function that calculates total price for a given order
    def get_total_price(self, order_id):
        result = (
            self.db.session.query(
                self.Order.id,
                func.sum(self.OrderProduct.quantity * self.Product.price).label('price')
            )
            .join(self.OrderProduct, self.OrderProduct.order_id == self.Order.id)
            .join(self.Product, self.Product.id == self.OrderProduct.product_id)
            .group_by(self.Order.id)
            .first()
        )

        if result:
            _, total_price = result
            return total_price
        return 0

    # function that returns all orders for a customer based on his email
    def get_orders(self, email):
        # create query
        orders = self.db.session.query(self.Order).filter(self.Order.email == email).all()

        result = {"orders": []}

        for order in orders:
            # initialize empty order data
            order_data = {
                "products": [],
                "price": 0.0,
                "status": order.status.value,
                "timestamp": order.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

            # fill order data with products and calculate the total prices
            total_price = 0.0
            for op in order.products:
                product = op.product
                product_data = {
                    "categories": [c.name for c in product.categories],
                    "name": product.name,
                    "price": float(product.price),
                    "quantity": op.quantity,
                }

                total_price += float(product.price) * op.quantity
                order_data["products"].append(product_data)

            order_data["price"] = round(total_price, 2)
            result["orders"].append(order_data)

        return result

    # function that confirms delivery for a given order in the  database
    def confirm_delivery(self, order_id):
        order = self.Order.query.filter_by(id=order_id).first()
        if order.status != self.OrderStatus.PENDING:
            return "Delivery not complete.", 400

        order.status = self.OrderStatus.COMPLETE
        self.db.session.commit()

        return "", 200