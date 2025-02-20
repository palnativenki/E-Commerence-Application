from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from app.routes import product_bp, order_bp

# Initialize the app, database, and marshmallow
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Register blueprints
app.register_blueprint(product_bp)
app.register_blueprint(order_bp)

if __name__ == '__main__':
    app.run(debug=True)
