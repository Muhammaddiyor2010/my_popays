"""
Script to initialize database with default products from JSON
"""
import asyncio
import json
from database import Database

async def init_products():
    """Initialize products from popaysadmin.json"""
    db = Database()
    await db.init_db()
    
    # Load products from JSON file
    try:
        with open('popaysadmin.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            products = data.get('products', [])
        
        print(f"Found {len(products)} products in JSON file")
        
        # Add products to database
        for product in products:
            try:
                product_id = await db.add_product(product)
                print(f"Added product: {product['name']} (ID: {product_id})")
            except Exception as e:
                print(f"Error adding product {product['name']}: {e}")
        
        print("✅ Products initialization completed!")
        
    except FileNotFoundError:
        print("❌ popaysadmin.json file not found!")
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")

async def init_admin_settings():
    """Initialize admin settings"""
    db = Database()
    
    # Set default admin settings
    settings = {
        'restaurant_name': 'Popays Fast Food',
        'min_order_amount': '100000',
        'free_delivery_amount': '50000',
        'working_hours': '24/7',
        'contact_phone': '+998 91 269 00 02'
    }
    
    for key, value in settings.items():
        await db.set_admin_setting(key, value)
        print(f"Set admin setting: {key} = {value}")
    
    print("✅ Admin settings initialization completed!")

async def main():
    """Main initialization function"""
    print("🚀 Initializing Popays Fast Food database...")
    
    await init_products()
    await init_admin_settings()
    
    print("🎉 Database initialization completed!")

if __name__ == "__main__":
    asyncio.run(main())
