from flask import jsonify
from app.exceptions import StockNotAvailableException

@app.errorhandler(StockNotAvailableException)
def handle_stock_not_available_error(error):
    return jsonify({'message': str(error)}), 400
