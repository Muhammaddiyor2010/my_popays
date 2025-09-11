import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = "popays.db"):
        self.db_path = db_path
        # Database'ni avtomatik yaratish
        self.init_db()

    def init_db(self):
        """Initialize database and create tables"""
        with sqlite3.connect(self.db_path) as db:
            # Products table
            db.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    stock INTEGER DEFAULT 0,
                    description TEXT,
                    img TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Orders table
            db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE NOT NULL,
                    branch TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    customer_location TEXT NOT NULL,
                    items TEXT NOT NULL,  -- JSON string
                    total INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    coordinates TEXT,  -- JSON string for location
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Contact messages table
            db.execute("""
                CREATE TABLE IF NOT EXISTS contact_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    customer_email TEXT,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'new',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Categories table
            db.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    display_order INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Admin settings table
            db.execute("""
                CREATE TABLE IF NOT EXISTS admin_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


            # Add description column if it doesn't exist (for existing databases)
            try:
                db.execute("ALTER TABLE products ADD COLUMN description TEXT")
            except sqlite3.OperationalError:
                # Column already exists, ignore error
                pass
            
            # Add img column if it doesn't exist (for existing databases)
            try:
                db.execute("ALTER TABLE products ADD COLUMN img TEXT")
            except sqlite3.OperationalError:
                # Column already exists, ignore error
                pass
            
            db.commit()

    def add_product(self, product_data: Dict) -> int:
        """Add a new product"""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute("""
                INSERT INTO products (name, price, category, stock, description, img)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                product_data['name'],
                product_data['price'],
                product_data.get('category', 'other'),
                product_data.get('stock', 0),
                product_data.get('description', ''),
                product_data.get('img', '')
            ))
            db.commit()
            return cursor.lastrowid

    def get_products(self) -> List[Dict]:
        """Get all products"""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute("""
                SELECT * FROM products ORDER BY id
            """)
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            products = []
            for row in rows:
                product = dict(zip(columns, row))
                products.append(product)
            
            return products

    def add_order(self, order_data: Dict) -> int:
        """Add a new order"""
        with sqlite3.connect(self.db_path) as db:
            import uuid
            order_id = str(uuid.uuid4())
            
            cursor = db.execute("""
                INSERT INTO orders (order_id, branch, customer_name, customer_phone, customer_location, items, total, coordinates)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                order_data['branch'],
                order_data['customer_name'],
                order_data['customer_phone'],
                order_data['customer_location'],
                json.dumps(order_data['items']),
                order_data['total'],
                json.dumps(order_data.get('coordinates', {}))
            ))
            db.commit()
            return cursor.lastrowid

    def get_orders(self, status: Optional[str] = None) -> List[Dict]:
        """Get orders by status"""
        with sqlite3.connect(self.db_path) as db:
            if status:
                cursor = db.execute("""
                    SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC
                """, (status,))
            else:
                cursor = db.execute("""
                    SELECT * FROM orders ORDER BY created_at DESC
                """)
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            orders = []
            for row in rows:
                order = dict(zip(columns, row))
                order['items'] = json.loads(order['items'])
                order['coordinates'] = json.loads(order['coordinates']) if order['coordinates'] else {}
                orders.append(order)
            
            return orders

    def add_contact_message(self, message_data: Dict) -> int:
        """Add a new contact message"""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute("""
                INSERT INTO contact_messages (customer_name, customer_phone, customer_email, message)
                VALUES (?, ?, ?, ?)
            """, (
                message_data['customer_name'],
                message_data['customer_phone'],
                message_data.get('customer_email'),
                message_data['message']
            ))
            db.commit()
            return cursor.lastrowid

    def get_contact_messages(self, status: Optional[str] = None) -> List[Dict]:
        """Get contact messages by status"""
        with sqlite3.connect(self.db_path) as db:
            if status:
                cursor = db.execute("""
                    SELECT * FROM contact_messages WHERE status = ? ORDER BY created_at DESC
                """, (status,))
            else:
                cursor = db.execute("""
                    SELECT * FROM contact_messages ORDER BY created_at DESC
                """)
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]

    def update_order_status(self, order_id: str, status: str):
        """Update order status"""
        with sqlite3.connect(self.db_path) as db:
            db.execute("""
                UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            """, (status, order_id))
            db.commit()

    def update_contact_status(self, message_id: int, status: str):
        """Update contact message status"""
        with sqlite3.connect(self.db_path) as db:
            db.execute("""
                UPDATE contact_messages SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, message_id))
            db.commit()

    def get_admin_setting(self, key: str) -> Optional[str]:
        """Get admin setting by key"""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute("""
                SELECT value FROM admin_settings WHERE key = ?
            """, (key,))
            row = cursor.fetchone()
            return row[0] if row else None

    def set_admin_setting(self, key: str, value: str):
        """Set admin setting"""
        with sqlite3.connect(self.db_path) as db:
            db.execute("""
                INSERT OR REPLACE INTO admin_settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            db.commit()

    def get_categories(self) -> List[Dict]:
        """Get all categories"""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute("""
                SELECT * FROM categories WHERE is_active = 1 ORDER BY display_order, name
            """)
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            categories = []
            for row in rows:
                category = dict(zip(columns, row))
                categories.append(category)
            
            return categories

    def add_category(self, category_data: Dict) -> int:
        """Add a new category"""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute("""
                INSERT INTO categories (name, description, display_order, is_active)
                VALUES (?, ?, ?, ?)
            """, (
                category_data['name'],
                category_data.get('description', ''),
                category_data.get('display_order', 0),
                category_data.get('is_active', 1)
            ))
            db.commit()
            return cursor.lastrowid

    def update_category(self, category_id: int, category_data: Dict):
        """Update a category"""
        with sqlite3.connect(self.db_path) as db:
            db.execute("""
                UPDATE categories SET 
                    name = ?, description = ?, display_order = ?, is_active = ?
                WHERE id = ?
            """, (
                category_data['name'],
                category_data.get('description', ''),
                category_data.get('display_order', 0),
                category_data.get('is_active', 1),
                category_id
            ))
            db.commit()

    def update_product_image(self, product_id: int, image_path: str):
        """Update product image"""
        with sqlite3.connect(self.db_path) as db:
            db.execute("""
                UPDATE products SET img = ? WHERE id = ?
            """, (image_path, product_id))
            db.commit()


    def delete_category(self, category_id: int):
        """Delete a category (soft delete by setting is_active to 0)"""
        with sqlite3.connect(self.db_path) as db:
            db.execute("""
                UPDATE categories SET is_active = 0 WHERE id = ?
            """, (category_id,))
            db.commit()

    def populate_products(self):
        """Populate database with default products"""
        products = [
            {"name": "Oddiy HotDog", "price": 8000, "category": "hotdog", "stock": 150, "description": "Oddiy hotdog - klassik ta'm va soddalik"},
            {"name": "HotDog dvaynoy", "price": 11000, "category": "hotdog", "stock": 150, "description": "Ikki xil kolbasa bilan tayyorlangan hotdog"},
            {"name": "HotDog kanatskiy", "price": 12000, "category": "hotdog", "stock": 150, "description": "Kanatskiy kolbasa bilan tayyorlangan hotdog"},
            {"name": "HotDog kanatskiy dvaynoy", "price": 15000, "category": "hotdog", "stock": 150, "description": "Ikki xil kanatskiy kolbasa bilan tayyorlangan hotdog"},
            {"name": "Go'shtli HotDog", "price": 25000, "category": "hotdog", "stock": 150, "description": "Go'shtli kolbasa bilan tayyorlangan hotdog"},
            {"name": "Longer", "price": 20000, "category": "hotdog", "stock": 150, "description": "Uzun hotdog - katta hajm va to'yingan ta'm"},
            {"name": "Longer Cheese", "price": 24000, "category": "hotdog", "stock": 150, "description": "Uzun hotdog pishloq bilan"},
            {"name": "BBQ burger", "price": 25000, "category": "burger", "stock": 150, "description": "BBQ sousi bilan tayyorlangan burger"},
            {"name": "Cheese burger", "price": 30000, "category": "burger", "stock": 150, "description": "Pishloq bilan tayyorlangan burger"},
            {"name": "BBQ burger halapeno", "price": 30000, "category": "burger", "stock": 150, "description": "BBQ sousi va halapeno bilan tayyorlangan burger"},
            {"name": "BBQ double burger", "price": 37000, "category": "burger", "stock": 150, "description": "Ikki xil go'sht va BBQ sousi bilan tayyorlangan burger"},
            {"name": "Double Cheese burger", "price": 45000, "category": "burger", "stock": 150, "description": "Ikki xil pishloq bilan tayyorlangan burger"},
            {"name": "Chicken Burger", "price": 23000, "category": "burger", "stock": 150, "description": "Tovuq go'shti bilan tayyorlangan burger"},
            {"name": "Chicken cheese", "price": 28000, "category": "burger", "stock": 150, "description": "Tovuq go'shti va pishloq bilan tayyorlangan burger"},
            {"name": "Oddiy Lavash", "price": 28000, "category": "lavash", "stock": 150, "description": "Oddiy lavash - klassik ta'm va soddalik"},
            {"name": "Extra Lavash", "price": 33000, "category": "lavash", "stock": 150, "description": "Qo'shimcha ingredientlar bilan tayyorlangan lavash"},
            {"name": "Cheese Lavash", "price": 28000, "category": "lavash", "stock": 150, "description": "Pishloq bilan tayyorlangan lavash"},
            {"name": "Extra cheese Lavash", "price": 38000, "category": "lavash", "stock": 150, "description": "Qo'shimcha pishloq bilan tayyorlangan lavash"},
            {"name": "Shaurma", "price": 20000, "category": "lavash", "stock": 150, "description": "Klassik shaurma - oddiy va mazali"},
            {"name": "Shaurma cheese", "price": 33000, "category": "lavash", "stock": 150, "description": "Pishloq bilan tayyorlangan shaurma"},
            {"name": "Shaurma extra", "price": 33000, "category": "lavash", "stock": 150, "description": "Qo'shimcha ingredientlar bilan tayyorlangan shaurma"},
            {"name": "Shaurma extra cheese", "price": 38000, "category": "lavash", "stock": 150, "description": "Qo'shimcha pishloq va ingredientlar bilan tayyorlangan shaurma"},
            {"name": "Strips", "price": 30000, "category": "sides", "stock": 150, "description": "Tovuq strips - qovurilgan tovuq bo'laklari"},
            {"name": "Fri", "price": 12000, "category": "sides", "stock": 150, "description": "Qovurilgan kartoshka - klassik ta'm"},
            {"name": "Suv", "price": 3000, "category": "drinks", "stock": 150, "description": "Toza suv - 0.5L"},
            {"name": "Twister Classic", "price": 25000, "category": "lavash", "stock": 150, "description": "Klassik twister - oddiy va mazali"},
            {"name": "Twister Cheese", "price": 30000, "category": "lavash", "stock": 150, "description": "Pishloq bilan tayyorlangan twister"},
            {"name": "Twister Spicy", "price": 28000, "category": "lavash", "stock": 150, "description": "Achchiq ta'mli twister"},
            {"name": "Combo Pizza Margherita", "price": 45000, "category": "combo", "stock": 150, "description": "Pizza Margherita + ichimlik + fri"},
            {"name": "Combo Pizza Pepperoni", "price": 50000, "category": "combo", "stock": 150, "description": "Pizza Pepperoni + ichimlik + fri"},
            {"name": "Combo Burger", "price": 35000, "category": "combo", "stock": 150, "description": "Burger + ichimlik + fri"},
            {"name": "Combo HotDog", "price": 25000, "category": "combo", "stock": 150, "description": "HotDog + ichimlik + fri"},
            {"name": "Combo Lavash", "price": 40000, "category": "combo", "stock": 150, "description": "Lavash + ichimlik + fri"}
        ]
        
        # Clear existing products
        with sqlite3.connect(self.db_path) as db:
            db.execute("DELETE FROM products")
            db.commit()
        
        # Add new products
        for product in products:
            self.add_product(product)
        
        print(f"Database'ga {len(products)} ta mahsulot qo'shildi!")

    def populate_categories(self):
        """Populate database with default categories"""
        categories = [
            {"name": "hotdog", "description": "HotDog mahsulotlari", "display_order": 1},
            {"name": "burger", "description": "Burger mahsulotlari", "display_order": 2},
            {"name": "lavash", "description": "Lavash va Shaurma mahsulotlari", "display_order": 3},
            {"name": "sides", "description": "Snacks va qo'shimcha taomlar", "display_order": 4},
            {"name": "drinks", "description": "Ichimliklar", "display_order": 5},
            {"name": "combo", "description": "Combo taomlar", "display_order": 6}
        ]
        
        # Clear existing categories
        with sqlite3.connect(self.db_path) as db:
            db.execute("DELETE FROM categories")
            db.commit()
        
        # Add new categories
        for category in categories:
            self.add_category(category)
        
        print(f"Database'ga {len(categories)} ta kategoriya qo'shildi!")

# Simple API server for categories and products
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=['http://127.0.0.1:5500', 'http://localhost:5500', 'http://127.0.0.1:3000', 'http://localhost:3000'])  # Enable CORS for specific origins

# Initialize database
db = Database()

@app.route('/api/categories', methods=['GET', 'OPTIONS'])
def get_categories():
    """API endpoint to get categories"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    try:
        categories = db.get_categories()
        response = jsonify(categories)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products', methods=['GET', 'POST', 'OPTIONS'])
def products_api():
    """API endpoint to get and add products"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    try:
        if request.method == 'GET':
            products = db.get_products()
            response = jsonify(products)
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        elif request.method == 'POST':
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'price', 'category']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Add product to database
            product_id = db.add_product(data)
            
            response = jsonify({
                "success": True, 
                "message": "Product added successfully",
                "product_id": product_id
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """API endpoint to update product"""
    try:
        data = request.get_json()
        
        # Update product in database
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.execute("""
                UPDATE products SET 
                    name = ?, price = ?, category = ?, description = ?
                WHERE id = ?
            """, (
                data.get('name'),
                data.get('price'),
                data.get('category'),
                data.get('description'),
                product_id
            ))
            conn.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Product not found"}), 404
        
        response = jsonify({"success": True, "message": "Product updated successfully"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """API endpoint to delete product"""
    try:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Product not found"}), 404
        
        response = jsonify({"success": True, "message": "Product deleted successfully"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<int:product_id>/image', methods=['PUT'])
def update_product_image(product_id):
    """API endpoint to update product image"""
    try:
        data = request.get_json()
        image_path = data.get('image_path', '')
        
        db.update_product_image(product_id, image_path)
        
        response = jsonify({"success": True, "message": "Product image updated successfully"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Database'ni avtomatik to'ldirish
if __name__ == "__main__":
    # Check if we should run the server or just populate data
    if len(os.sys.argv) > 1 and os.sys.argv[1] == 'server':
        print("Starting API server on http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        db.populate_products()
        db.populate_categories()
