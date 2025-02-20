import pytest
from app import app, db
from app.models import Product

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.create_all()
    yield app.test_client()
    db.session.remove()
    db.drop_all()

def test_get_products(client):
    response = client.get('/products')
    assert response.status_code == 200

def test_add_product(client):
    response = client.post('/products', json={
        'name': 'Test Product',
        'description': 'Test description',
        'price': 19.99,
        'stock': 10
    })
    assert response.status_code == 201
