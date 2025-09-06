import aiosqlite
import json
from datetime import datetime
from typing import List, Dict, Optional
import config

class Database:
    def __init__(self, db_path: str = "popays.db"):
        self.db_path = db_path

    async def init_db(self):
        """Initialize database and create tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Products table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    image TEXT,
                    description TEXT,
                    badge TEXT,
                    stock INTEGER DEFAULT 0,
                    sizes TEXT,  -- JSON string for sizes
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Orders table
            await db.execute("""
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
            await db.execute("""
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
            await db.execute("""
                CREATE TABLE IF NOT EXISTS admin_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await db.commit()

    async def add_product(self, product_data: Dict) -> int:
        """Add a new product"""
        async with aiosqlite.connect(self.db_path) as db:
            sizes_json = json.dumps(product_data.get('sizes', [])) if product_data.get('sizes') else None
            
            cursor = await db.execute("""
                INSERT INTO products (name, price, category, image, description, badge, stock, sizes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data['name'],
                product_data['price'],
                product_data['category'],
                product_data.get('image'),
                product_data.get('description'),
                product_data.get('badge'),
                product_data.get('stock', 0),
                sizes_json
            ))
            await db.commit()
            return cursor.lastrowid

    async def get_products(self, category: Optional[str] = None) -> List[Dict]:
        """Get all products or products by category"""
        async with aiosqlite.connect(self.db_path) as db:
            if category:
                cursor = await db.execute("""
                    SELECT * FROM products WHERE category = ? ORDER BY id
                """, (category,))
            else:
                cursor = await db.execute("""
                    SELECT * FROM products ORDER BY id
                """)
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            products = []
            for row in rows:
                product = dict(zip(columns, row))
                if product['sizes']:
                    product['sizes'] = json.loads(product['sizes'])
                products.append(product)
            
            return products

    async def add_order(self, order_data: Dict) -> int:
        """Add a new order"""
        async with aiosqlite.connect(self.db_path) as db:
            import uuid
            order_id = str(uuid.uuid4())
            
            cursor = await db.execute("""
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
            await db.commit()
            return cursor.lastrowid

    async def get_orders(self, status: Optional[str] = None) -> List[Dict]:
        """Get orders by status"""
        async with aiosqlite.connect(self.db_path) as db:
            if status:
                cursor = await db.execute("""
                    SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC
                """, (status,))
            else:
                cursor = await db.execute("""
                    SELECT * FROM orders ORDER BY created_at DESC
                """)
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            orders = []
            for row in rows:
                order = dict(zip(columns, row))
                order['items'] = json.loads(order['items'])
                order['coordinates'] = json.loads(order['coordinates']) if order['coordinates'] else {}
                orders.append(order)
            
            return orders

    async def add_contact_message(self, message_data: Dict) -> int:
        """Add a new contact message"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO contact_messages (customer_name, customer_phone, customer_email, message)
                VALUES (?, ?, ?, ?)
            """, (
                message_data['customer_name'],
                message_data['customer_phone'],
                message_data.get('customer_email'),
                message_data['message']
            ))
            await db.commit()
            return cursor.lastrowid

    async def get_contact_messages(self, status: Optional[str] = None) -> List[Dict]:
        """Get contact messages by status"""
        async with aiosqlite.connect(self.db_path) as db:
            if status:
                cursor = await db.execute("""
                    SELECT * FROM contact_messages WHERE status = ? ORDER BY created_at DESC
                """, (status,))
            else:
                cursor = await db.execute("""
                    SELECT * FROM contact_messages ORDER BY created_at DESC
                """)
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]

    async def update_order_status(self, order_id: str, status: str):
        """Update order status"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            """, (status, order_id))
            await db.commit()

    async def update_contact_status(self, message_id: int, status: str):
        """Update contact message status"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE contact_messages SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, message_id))
            await db.commit()

    async def get_admin_setting(self, key: str) -> Optional[str]:
        """Get admin setting by key"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT value FROM admin_settings WHERE key = ?
            """, (key,))
            row = await cursor.fetchone()
            return row[0] if row else None

    async def set_admin_setting(self, key: str, value: str):
        """Set admin setting"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO admin_settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            await db.commit()
