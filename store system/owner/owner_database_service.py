from sqlalchemy import func, case

class OwnerDatabaseService:
    def __init__(self, db, Product, Category, Order, OrderProduct, OrderStatus, ProductCategory):
        self.db = db
        self.Product = Product
        self.Category = Category
        self.Order = Order
        self.OrderProduct = OrderProduct
        self.OrderStatus = OrderStatus
        self.ProductCategory = ProductCategory

    # function that adds given products to the database
    def add_products(self, products):
        added = []
        for index, entry in enumerate(products):
            categories, name, price = entry
            # check if the price is float and greater than 0
            try:
                price = float(price)
            except ValueError:
                return f"Incorrect price on line {index}.", 400

            if price < 0:
                return f"Incorrect price on line {index}.", 400

            price = float(price)

            # check if the product already exists
            product_record = self.Product.query.filter_by(name=name).first()
            if product_record:
                return f"Product {name} already exists.", 400

            # create a product
            product = self.Product(name=name, price=price)

            # check if any of the categories is missing and add it to the databases
            cat_objs = []
            for cat in categories:
                category = self.Category.query.filter_by(name=cat).first()
                if not category:
                    category = self.Category(name=cat)
                    self.db.session.add(category)
                    self.db.session.flush()
                cat_objs.append(category)

            product.categories = cat_objs
            added.append(product)

        # insert every product to the database
        for product in added:
            self.db.session.add(product)
            self.db.session.commit()

        return "", 200

    # function that returns product statistics
    def product_stats(self):
        # create and execute query
        stats = (
            self.db.session.query(
                self.Product.name,
                func.sum(
                    case((self.Order.status == "COMPLETE", self.OrderProduct.quantity), else_=0)
                ).label("sold"),
                func.sum(
                    case((self.Order.status != "COMPLETE", self.OrderProduct.quantity), else_=0)
                ).label("waiting")
            )
            .join(self.OrderProduct)
            .join(self.Order)
            .group_by(self.Product.id)
        )

        # format the result
        stats = [
            {"name": name, "sold": int(sold or 0), "waiting": int(waiting or 0)}
            for name, sold, waiting in stats.all()
            if (sold or 0) + (waiting or 0) > 0
        ]

        return stats

    # function that returns category statistics
    def category_stats(self):
        # create and execute query
        delivered = func.coalesce(
            func.sum(case((self.Order.status == "COMPLETE", self.OrderProduct.quantity), else_=0)), 0
        ).label("delivered")
        stats = (
            self.db.session.query(self.Category.name, delivered)
            .outerjoin(self.ProductCategory, self.ProductCategory.category_id == self.Category.id)
            .outerjoin(self.Product, self.Product.id == self.ProductCategory.product_id)
            .outerjoin(self.OrderProduct, self.OrderProduct.product_id == self.Product.id)
            .outerjoin(self.Order, self.Order.id == self.OrderProduct.order_id)
            .group_by(self.Category.id)
            .order_by(delivered.desc(), self.Category.name.asc())
        )

        # format the result
        stats = [name for name, _ in stats.all()]

        return stats