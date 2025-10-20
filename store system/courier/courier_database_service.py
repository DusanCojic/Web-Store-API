
class CourierDatabaseService:
    def __init__(self, db, Product, Category, Order, OrderProduct, OrderStatus, ProductCategory):
        self.db = db
        self.Product = Product
        self.Category = Category
        self.Order = Order
        self.OrderProduct = OrderProduct
        self.OrderStatus = OrderStatus
        self.ProductCategory = ProductCategory

    # function that returns all orders that have not been picked by any courier
    def orders_to_deliver(self):
        orders = self.db.session.query(self.Order).filter(
            self.Order.status == self.OrderStatus.CREATED)
        orders = [{"id": order.id, "email": order.email} for order in orders]
        return orders

    # function that checks if order exists
    def check_order(self, order_id):
        order = self.Order.query.filter_by(id=order_id).first()
        if not order or order.status != self.OrderStatus.CREATED:
            return "Invalid order id.", 400

        return "", 200

    # function that marks order as picked based on order id
    def pick_up_order(self, id):
        order = self.Order.query.filter_by(id=id).first()
        order.status = self.OrderStatus.PENDING
        self.db.session.add(order)
        self.db.session.commit()

    # function that returns address of a smart contract related to the given order
    def get_address(self, order_id):
        order = self.Order.query.filter_by(id=order_id).first()
        return order.address