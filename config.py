import os
from dotenv import load_dotenv

load_dotenv()

# Cloudflare API credentials
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN', '')
CLOUDFLARE_EMAIL = os.getenv('CLOUDFLARE_EMAIL', '')
CLOUDFLARE_API_KEY = os.getenv('CLOUDFLARE_API_KEY', '')

# Registrar API credentials (example - adjust based on your registrar)
REGISTRAR_API_URL = os.getenv('REGISTRAR_API_URL', '')
REGISTRAR_API_KEY = os.getenv('REGISTRAR_API_KEY', '')
REGISTRAR_API_SECRET = os.getenv('REGISTRAR_API_SECRET', '')

# Cloudflare API base URL
CLOUDFLARE_API_BASE = 'https://api.cloudflare.com/client/v4'

