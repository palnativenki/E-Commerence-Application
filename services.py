from app.models import db, Product, Order
from flask import jsonify

def add_product(data):
    try:
        new_product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            stock=data['stock']
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

def place_order(data):
    try:
        order_total = 0
        order_products = []

        for item in data['products']:
            product = Product.query.get(item['product_id'])
            if product is None:
                return jsonify({'error': f"Product {item['product_id']} not found"}), 404
            if product.stock < item['quantity']:
                return jsonify({'error': f"Insufficient stock for {product.name}"}), 400

            product.stock -= item['quantity']
            order_total += product.price * item['quantity']
            order_products.append({'product_id': product.id, 'quantity': item['quantity']})

        new_order = Order(
            total_price=order_total,
            status='pending'
        )
        db.session.add(new_order)
        db.session.commit()

        for item in order_products:
            db.session.execute('INSERT INTO order_product (order_id, product_id, quantity) VALUES (?, ?, ?)',
                               (new_order.id, item['product_id'], item['quantity']))

        db.session.commit()

        return jsonify({'message': 'Order placed successfully', 'total_price': order_total}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
