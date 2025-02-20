import pytest
from app import app, db
from app.models import Product, Order

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.create_all()
    yield app.test_client()
    db.session.remove()
    db.drop_all()

def test_place_order(client):
    product = Product(name='Test Product', description='Test desc', price=19.99, stock=10)
    db.session.add(product)
    db.session.commit()

    response = client.post('/orders', json={
        'products': [{'product_id': product.id, 'quantity': 2}]
    })
    assert response.status_code == 201
