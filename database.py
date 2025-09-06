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

            db.commit()

    def add_product(self, product_data: Dict) -> int:
        """Add a new product"""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute("""
                INSERT INTO products (name, price, category, stock)
                VALUES (?, ?, ?, ?)
            """, (
                product_data['name'],
                product_data['price'],
                product_data.get('category', 'other'),
                product_data.get('stock', 0)
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
