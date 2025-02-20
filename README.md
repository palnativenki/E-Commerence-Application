Flask==2.2.2
Flask-RESTful==0.3.9
Flask-SQLAlchemy==2.5.1
pytest==7.2.0

# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Product {self.name}>"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    products = db.Column(db.JSON, nullable=False)  # List of products with quantities
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')

    def __repr__(self):
        return f"<Order {self.id} - {self.status}>"

# app.py

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from models import db, Product, Order
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
api = Api(app)

# Endpoint: GET /products
class ProductList(Resource):
    def get(self):
        products = Product.query.all()
        return jsonify([{
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock
        } for product in products])

# Endpoint: POST /products
class ProductCreate(Resource):
    def post(self):
        data = request.get_json()

        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        stock = data.get('stock')

        if not name or not description or not price or not stock:
            return {'error': 'Missing fields'}, 400

        new_product = Product(name=name, description=description, price=price, stock=stock)

        try:
            db.session.add(new_product)
            db.session.commit()
            return jsonify({'message': 'Product added successfully', 'product': new_product.id})
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Product already exists'}, 400

# Endpoint: POST /orders
class OrderCreate(Resource):
    def post(self):
        data = request.get_json()
        product_quantities = data.get('products')  # [{'id': 1, 'quantity': 2}, ...]

        if not product_quantities:
            return {'error': 'No products in order'}, 400

        total_price = 0
        for item in product_quantities:
            product = Product.query.get(item['id'])
            if not product:
                return {'error': f'Product with ID {item["id"]} not found'}, 404

            if product.stock < item['quantity']:
                return {'error': f'Insufficient stock for product {product.name}'}, 400

            product.stock -= item['quantity']
            total_price += product.price * item['quantity']

        # Create order
        new_order = Order(products=product_quantities, total_price=total_price)

        try:
            db.session.add(new_order)
            db.session.commit()
            db.session.flush()  # Ensures the ID is available after commit
            return jsonify({'message': 'Order placed successfully', 'order_id': new_order.id})
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Error placing order'}, 500

api.add_resource(ProductList, '/products')
api.add_resource(ProductCreate, '/products')
api.add_resource(OrderCreate, '/orders')

if __name__ == '__main__':
    app.run(debug=True)


# Dockerfile

# Use the official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]


# test_app.py

import pytest
from app import app, db, Product, Order

@pytest.fixture
def client():
    with app.test_client() as client:
        db.create_all()  # Create tables before each test
        yield client
        db.drop_all()  # Clean up after tests

def test_get_products(client):
    response = client.get('/products')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_product(client):
    response = client.post('/products', json={
        'name': 'Test Product', 'description': 'Test Desc', 'price': 19.99, 'stock': 100
    })
    assert response.status_code == 200
    assert 'product' in response.json

def test_create_order(client):
    client.post('/products', json={'name': 'Test Product', 'description': 'Test Desc', 'price': 19.99, 'stock': 100})
    response = client.post('/orders', json={
        'products': [{'id': 1, 'quantity': 2}]
    })
    assert response.status_code == 200
    assert 'order_id' in response.json

docker build -t ecommerce-api .
docker run -p 5000:5000 ecommerce-api

    

        

