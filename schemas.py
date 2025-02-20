from app import ma
from app.models import Product, Order

# Product schema
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

# Order schema
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
