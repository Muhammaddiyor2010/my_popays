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
            
            db.commit()

    def add_product(self, product_data: Dict) -> int:
        """Add a new product"""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute("""
                INSERT INTO products (name, price, category, stock, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product_data['name'],
                product_data['price'],
                product_data.get('category', 'other'),
                product_data.get('stock', 0),
                product_data.get('description', '')
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
            {"name": "Twister Classic", "price": 25000, "category": "twister", "stock": 150, "description": "Klassik twister - oddiy va mazali"},
            {"name": "Twister Cheese", "price": 30000, "category": "twister", "stock": 150, "description": "Pishloq bilan tayyorlangan twister"},
            {"name": "Twister Spicy", "price": 28000, "category": "twister", "stock": 150, "description": "Achchiq ta'mli twister"},
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

# Database'ni avtomatik to'ldirish
if __name__ == "__main__":
    db = Database()
    db.populate_products()
