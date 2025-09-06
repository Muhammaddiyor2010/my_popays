# Popays Fast Food Bot

Aiogram va SQLite yordamida yaratilgan Telegram bot.

## O'rnatish

1. **Kerakli paketlarni o'rnating:**
```bash
pip install -r requirements.txt
```

2. **Konfiguratsiya faylini yarating:**
```bash
cp .env.example .env
```

3. **`.env` faylini to'ldiring:**
```env
BOT_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_admin_chat_id_here
DATABASE_URL=sqlite:///popays.db
RESTAURANT_NAME=Popays Fast Food
```

4. **Ma'lumotlar bazasini ishga tushiring:**
```bash
python init_data.py
```

5. **Botni ishga tushiring:**
```bash
python bot.py
```

6. **Webhook serverini ishga tushiring (ixtiyoriy):**
```bash
python webhook_server.py
```

## Fayllar

- `bot.py` - Asosiy bot fayli
- `database.py` - Ma'lumotlar bazasi operatsiyalari
- `config.py` - Konfiguratsiya
- `webhook_server.py` - Webhook server
- `init_data.py` - Ma'lumotlar bazasini ishga tushirish
- `requirements.txt` - Kerakli paketlar

## Funksiyalar

### Bot Komandalari
- `/start` - Botni ishga tushirish
- `/admin` - Admin panel

### Admin Panel
- 📊 Statistika
- 📦 Buyurtmalar
- ✉️ Xabarlar
- 🍽️ Mahsulotlar

### Ma'lumotlar Bazasi
- **products** - Mahsulotlar
- **orders** - Buyurtmalar
- **contact_messages** - Aloqa xabarlari
- **admin_settings** - Admin sozlamalari

## Web App Integratsiyasi

Bot web app'dan kelgan ma'lumotlarni qabul qiladi:
- Buyurtma ma'lumotlari
- Aloqa xabarlari
- Lokatsiya ma'lumotlari

## Ishlatish

1. Bot tokenini oling: [@BotFather](https://t.me/BotFather)
2. Admin chat ID ni oling: [@userinfobot](https://t.me/userinfobot)
3. Konfiguratsiyani to'ldiring
4. Botni ishga tushiring
