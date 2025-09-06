import asyncio
import json
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Initialize database
db = Database()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Start command handler"""
    await message.answer(
        f"🍔 <b>{config.RESTAURANT_NAME} Bot</b>\n\n"
        "Assalomu alaykum! Men Popays Fast Food botiman.\n"
        "Buyurtma berish va aloqa uchun botdan foydalaning.\n\n"
        "📱 <b>Buyurtma berish:</b> Web App orqali\n"
        "✉️ <b>Aloqa:</b> Xabar yuborish\n"
        "📞 <b>Qo'llab-quvvatlash:</b> 24/7",
        parse_mode="HTML"
    )

@dp.message(Command("admin"))
async def admin_command(message: types.Message):
    """Admin command handler"""
    if str(message.from_user.id) != config.ADMIN_CHAT_ID:
        await message.answer("❌ Sizda admin huquqi yo'q!")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📦 Buyurtmalar", callback_data="admin_orders")],
        [InlineKeyboardButton(text="✉️ Xabarlar", callback_data="admin_messages")],
        [InlineKeyboardButton(text="🍽️ Mahsulotlar", callback_data="admin_products")]
    ])
    
    await message.answer(
        "🔧 <b>Admin Panel</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    """Admin statistics"""
    if str(callback.from_user.id) != config.ADMIN_CHAT_ID:
        await callback.answer("❌ Sizda admin huquqi yo'q!", show_alert=True)
        return
    
    # Get statistics
    orders = await db.get_orders()
    messages = await db.get_contact_messages()
    products = await db.get_products()
    
    pending_orders = len([o for o in orders if o['status'] == 'pending'])
    new_messages = len([m for m in messages if m['status'] == 'new'])
    
    stats_text = (
        "📊 <b>Statistika</b>\n\n"
        f"📦 <b>Jami buyurtmalar:</b> {len(orders)}\n"
        f"⏳ <b>Kutilayotgan:</b> {pending_orders}\n"
        f"✉️ <b>Jami xabarlar:</b> {len(messages)}\n"
        f"🆕 <b>Yangi xabarlar:</b> {new_messages}\n"
        f"🍽️ <b>Mahsulotlar:</b> {len(products)}\n\n"
        f"📅 <b>Oxirgi yangilanish:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    
    await callback.message.edit_text(stats_text, parse_mode="HTML")

@dp.callback_query(F.data == "admin_orders")
async def admin_orders(callback: types.CallbackQuery):
    """Admin orders list"""
    if str(callback.from_user.id) != config.ADMIN_CHAT_ID:
        await callback.answer("❌ Sizda admin huquqi yo'q!", show_alert=True)
        return
    
    orders = await db.get_orders()
    
    if not orders:
        await callback.message.edit_text("📦 Hozircha buyurtmalar yo'q.")
        return
    
    # Show last 5 orders
    recent_orders = orders[:5]
    orders_text = "📦 <b>So'nggi buyurtmalar:</b>\n\n"
    
    for order in recent_orders:
        status_emoji = "⏳" if order['status'] == 'pending' else "✅" if order['status'] == 'completed' else "❌"
        orders_text += (
            f"{status_emoji} <b>#{order['id']}</b>\n"
            f"👤 {order['customer_name']}\n"
            f"📞 {order['customer_phone']}\n"
            f"🏪 {config.BRANCHES.get(order['branch'], order['branch'])}\n"
            f"💰 {order['total']:,} so'm\n"
            f"📅 {order['created_at'][:16]}\n\n"
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
    ])
    
    await callback.message.edit_text(orders_text, reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(F.data == "admin_messages")
async def admin_messages(callback: types.CallbackQuery):
    """Admin messages list"""
    if str(callback.from_user.id) != config.ADMIN_CHAT_ID:
        await callback.answer("❌ Sizda admin huquqi yo'q!", show_alert=True)
        return
    
    messages = await db.get_contact_messages()
    
    if not messages:
        await callback.message.edit_text("✉️ Hozircha xabarlar yo'q.")
        return
    
    # Show last 5 messages
    recent_messages = messages[:5]
    messages_text = "✉️ <b>So'nggi xabarlar:</b>\n\n"
    
    for msg in recent_messages:
        status_emoji = "🆕" if msg['status'] == 'new' else "✅" if msg['status'] == 'read' else "📝"
        messages_text += (
            f"{status_emoji} <b>#{msg['id']}</b>\n"
            f"👤 {msg['customer_name']}\n"
            f"📞 {msg['customer_phone']}\n"
            f"💬 {msg['message'][:50]}...\n"
            f"📅 {msg['created_at'][:16]}\n\n"
        )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")]
    ])
    
    await callback.message.edit_text(messages_text, reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: types.CallbackQuery):
    """Back to admin menu"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📦 Buyurtmalar", callback_data="admin_orders")],
        [InlineKeyboardButton(text="✉️ Xabarlar", callback_data="admin_messages")],
        [InlineKeyboardButton(text="🍽️ Mahsulotlar", callback_data="admin_products")]
    ])
    
    await callback.message.edit_text(
        "🔧 <b>Admin Panel</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

async def process_order_data(order_data: dict):
    """Process order data from web app"""
    try:
        # Save order to database
        order_id = await db.add_order({
            'branch': order_data.get('branch', 'kosmonavt'),
            'customer_name': order_data['customer']['name'],
            'customer_phone': order_data['customer']['phone'],
            'customer_location': order_data['customer']['location'],
            'items': order_data['items'],
            'total': order_data['total'],
            'coordinates': order_data.get('mapData', {}).get('coordinates', {})
        })
        
        # Format order message
        branch_name = config.BRANCHES.get(order_data.get('branch', 'kosmonavt'), 'Kosmonavt')
        items_text = "\n".join([f"• {item['name']} x{item['quantity']} - {item['total']:,} so'm" for item in order_data['items']])
        
        # Add map links if available
        map_links = ""
        if order_data.get('mapData', {}).get('mapLinks'):
            map_links = f"\n\n🗺️ <b>Xarita:</b>\n"
            for map_type, url in order_data['mapData']['mapLinks'].items():
                map_links += f"📍 {map_type.title()}: {url}\n"
        
        order_message = (
            f"🍔 <b>YANGI BUYURTMA #{order_id}</b>\n\n"
            f"🏪 <b>Filial:</b> {branch_name}\n"
            f"👤 <b>Mijoz:</b> {order_data['customer']['name']}\n"
            f"📞 <b>Telefon:</b> {order_data['customer']['phone']}\n"
            f"📍 <b>Lokatsiya:</b> {order_data['customer']['location']}\n\n"
            f"🛒 <b>Buyurtma:</b>\n{items_text}\n\n"
            f"💰 <b>Jami:</b> {order_data['total']:,} so'm{map_links}\n\n"
            f"⏰ <b>Vaqt:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        
        # Send to admin
        await bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=order_message,
            parse_mode="HTML"
        )
        
        logger.info(f"Order #{order_id} processed and sent to admin")
        
    except Exception as e:
        logger.error(f"Error processing order: {e}")

async def process_contact_data(contact_data: dict):
    """Process contact message from web app"""
    try:
        # Save contact message to database
        message_id = await db.add_contact_message({
            'customer_name': contact_data['customer']['name'],
            'customer_phone': contact_data['customer']['phone'],
            'customer_email': contact_data['customer'].get('email'),
            'message': contact_data['message']
        })
        
        # Format contact message
        contact_message = (
            f"✉️ <b>YANGI XABAR #{message_id}</b>\n\n"
            f"👤 <b>Mijoz:</b> {contact_data['customer']['name']}\n"
            f"📞 <b>Telefon:</b> {contact_data['customer']['phone']}\n"
            f"📧 <b>Email:</b> {contact_data['customer'].get('email', 'Kiritilmagan')}\n\n"
            f"💬 <b>Xabar:</b>\n{contact_data['message']}\n\n"
            f"⏰ <b>Vaqt:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        
        # Send to admin
        await bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=contact_message,
            parse_mode="HTML"
        )
        
        logger.info(f"Contact message #{message_id} processed and sent to admin")
        
    except Exception as e:
        logger.error(f"Error processing contact message: {e}")

async def main():
    """Main function"""
    # Initialize database
    await db.init_db()
    logger.info("Database initialized")
    
    # Start bot
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
