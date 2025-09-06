import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', 'YOUR_ADMIN_CHAT_ID_HERE')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///popays.db')

# Restaurant Configuration
RESTAURANT_NAME = os.getenv('RESTAURANT_NAME', 'Popays Fast Food')

# Branch Configuration
BRANCHES = {
    'kosmonavt': 'Kosmonavt',
    'derizli': 'Derizli Kosmonavt'
}
