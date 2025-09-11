import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://127.0.0.1:5500', 'http://localhost:5500', 'http://127.0.0.1:3000', 'http://localhost:3000'])

# File paths
CATEGORIES_FILE = 'categories.json'
PRODUCTS_FILE = 'products.json'

def load_json_data(filename):
    """Load data from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

def save_json_data(filename, data):
    """Save data to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

@app.route('/api/categories')
def get_categories():
    """API endpoint to get categories"""
    try:
        categories = load_json_data(CATEGORIES_FILE)
        # Filter active categories
        active_categories = [cat for cat in categories if cat.get('is_active', 1) == 1]
        # Sort by display_order
        active_categories.sort(key=lambda x: x.get('display_order', 0))
        
        response = jsonify(active_categories)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products')
def get_products():
    """API endpoint to get products"""
    try:
        products = load_json_data(PRODUCTS_FILE)
        response = jsonify(products)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories', methods=['POST'])
def add_category():
    """API endpoint to add a new category"""
    try:
        data = request.get_json()
        categories = load_json_data(CATEGORIES_FILE)
        
        # Generate new ID
        new_id = max([cat.get('id', 0) for cat in categories], default=0) + 1
        
        new_category = {
            'id': new_id,
            'name': data.get('name'),
            'description': data.get('description', ''),
            'display_order': data.get('display_order', 0),
            'is_active': data.get('is_active', 1),
            'created_at': '2025-09-10 17:21:43'
        }
        
        categories.append(new_category)
        
        if save_json_data(CATEGORIES_FILE, categories):
            return jsonify(new_category), 201
        else:
            return jsonify({"error": "Failed to save category"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    """API endpoint to add a new product"""
    try:
        data = request.get_json()
        products = load_json_data(PRODUCTS_FILE)
        
        # Generate new ID
        new_id = max([prod.get('id', 0) for prod in products], default=0) + 1
        
        new_product = {
            'id': new_id,
            'name': data.get('name'),
            'price': data.get('price'),
            'category': data.get('category', 'other'),
            'stock': data.get('stock', 0),
            'description': data.get('description', ''),
            'img': data.get('img', '')
        }
        
        products.append(new_product)
        
        if save_json_data(PRODUCTS_FILE, products):
            return jsonify(new_product), 201
        else:
            return jsonify({"error": "Failed to save product"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """API endpoint to update a category"""
    try:
        data = request.get_json()
        categories = load_json_data(CATEGORIES_FILE)
        
        for i, category in enumerate(categories):
            if category.get('id') == category_id:
                categories[i].update({
                    'name': data.get('name', category.get('name')),
                    'description': data.get('description', category.get('description')),
                    'display_order': data.get('display_order', category.get('display_order')),
                    'is_active': data.get('is_active', category.get('is_active'))
                })
                
                if save_json_data(CATEGORIES_FILE, categories):
                    return jsonify(categories[i])
                else:
                    return jsonify({"error": "Failed to save category"}), 500
        
        return jsonify({"error": "Category not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """API endpoint to update a product"""
    try:
        data = request.get_json()
        products = load_json_data(PRODUCTS_FILE)
        
        for i, product in enumerate(products):
            if product.get('id') == product_id:
                products[i].update({
                    'name': data.get('name', product.get('name')),
                    'price': data.get('price', product.get('price')),
                    'category': data.get('category', product.get('category')),
                    'stock': data.get('stock', product.get('stock')),
                    'description': data.get('description', product.get('description')),
                    'img': data.get('img', product.get('img'))
                })
                
                if save_json_data(PRODUCTS_FILE, products):
                    return jsonify(products[i])
                else:
                    return jsonify({"error": "Failed to save product"}), 500
        
        return jsonify({"error": "Product not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """API endpoint to delete a category (soft delete)"""
    try:
        categories = load_json_data(CATEGORIES_FILE)
        
        for i, category in enumerate(categories):
            if category.get('id') == category_id:
                categories[i]['is_active'] = 0
                
                if save_json_data(CATEGORIES_FILE, categories):
                    return jsonify({"message": "Category deleted successfully"})
                else:
                    return jsonify({"error": "Failed to save category"}), 500
        
        return jsonify({"error": "Category not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """API endpoint to delete a product"""
    try:
        products = load_json_data(PRODUCTS_FILE)
        
        for i, product in enumerate(products):
            if product.get('id') == product_id:
                del products[i]
                
                if save_json_data(PRODUCTS_FILE, products):
                    return jsonify({"message": "Product deleted successfully"})
                else:
                    return jsonify({"error": "Failed to save product"}), 500
        
        return jsonify({"error": "Product not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting JSON-based API server on http://localhost:5000")
    print("Categories and products are now stored in JSON files")
    app.run(debug=True, host='0.0.0.0', port=5000)
