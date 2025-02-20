from flask import Blueprint, request, jsonify
from app import db
from app.models import Product, Order, OrderProduct
from app.schemas import ProductSchema, OrderSchema
from app.exceptions import StockNotAvailableException

product_bp = Blueprint('product', __name__, url_prefix='/products')
order_bp = Blueprint('order', __name__, url_prefix='/orders')

# Route to get all products
@product_bp.route('', methods=['GET'])
def get_products():
    products = Product.query.all()
    product_schema = ProductSchema(many=True)
    return jsonify(product_schema.dump(products))

# Route to add a new product
@product_bp.route('', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        stock=data['stock']
    )
    db.session.add(new_product)
    db.session.commit()
    product_schema = ProductSchema()
    return jsonify(product_schema.dump(new_product)), 201

# Route to place an order
@order_bp.route('', methods=['POST'])
def place_order():
    data = request.get_json()
    products_in_order = data['products']
    
    total_price = 0
    order_products = []

    # Check stock and calculate total price
    for item in products_in_order:
        product = Product.query.get(item['product_id'])
        if product and product.stock >= item['quantity']:
            product.stock -= item['quantity']
            total_price += product.price * item['quantity']
            order_product = OrderProduct(product_id=product.id, quantity=item['quantity'])
            order_products.append(order_product)
        else:
            raise StockNotAvailableException("Not enough stock available.")

    # Create order and commit to DB
    new_order = Order(total_price=total_price)
    db.session.add(new_order)
    db.session.commit()

    # Associate products with order
    for order_product in order_products:
        order_product.order_id = new_order.id
    db.session.add_all(order_products)
    db.session.commit()

    order_schema = OrderSchema()
    return jsonify(order_schema.dump(new_order)), 201

