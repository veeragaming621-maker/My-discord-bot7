import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('DISCORD_TOKEN')
BOT_PREFIX = '!'
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot.db')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

COLORS = {
    'success': 0x00ff00,
    'error': 0xff0000,
    'warning': 0xffff00,
    'info': 0x0099ff,
    'embed': 0x2f3136,
}