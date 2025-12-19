import os
from dotenv import load_dotenv

load_dotenv()

# Cloudflare API credentials - используем Global API Key
CLOUDFLARE_EMAIL = os.getenv('CLOUDFLARE_EMAIL', '')
CLOUDFLARE_API_KEY = os.getenv('CLOUDFLARE_API_KEY', '')

# Ukraine.com.ua API credentials - только API ключ
REGISTRAR_API_URL = os.getenv('REGISTRAR_API_URL', 'https://api.ukraine.com.ua/v2')
REGISTRAR_API_KEY = os.getenv('REGISTRAR_API_KEY', '')

# Cloudflare API base URL
CLOUDFLARE_API_BASE = 'https://api.cloudflare.com/client/v4'

