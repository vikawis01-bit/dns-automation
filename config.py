import os
import json
from dotenv import load_dotenv

load_dotenv()

# Путь к файлу настроек
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

def load_settings_from_file():
    """Загрузка настроек из файла settings.json"""
    settings = {}
    
    # Сначала загружаем из переменных окружения
    settings['CLOUDFLARE_EMAIL'] = os.getenv('CLOUDFLARE_EMAIL', '')
    settings['CLOUDFLARE_API_KEY'] = os.getenv('CLOUDFLARE_API_KEY', '')
    settings['REGISTRAR_API_URL'] = os.getenv('REGISTRAR_API_URL', 'https://www.ukraine.com.ua/api/v2')
    settings['REGISTRAR_API_KEY'] = os.getenv('REGISTRAR_API_KEY', '')
    
    # Затем перезаписываем из файла, если он существует
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                file_settings = json.load(f)
                settings.update(file_settings)
        except Exception as e:
            print(f"Ошибка загрузки настроек из файла: {e}")
    
    return settings

def save_settings_to_file(settings):
    """Сохранение настроек в файл settings.json"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка сохранения настроек: {e}")
        return False

# Загружаем настройки
_settings = load_settings_from_file()

# Cloudflare API credentials - используем Global API Key
CLOUDFLARE_EMAIL = _settings.get('CLOUDFLARE_EMAIL', '')
CLOUDFLARE_API_KEY = _settings.get('CLOUDFLARE_API_KEY', '')

# Ukraine.com.ua API credentials - только API ключ (токен)
# Базовый URL: https://adm.tools/action/
REGISTRAR_API_URL = _settings.get('REGISTRAR_API_URL', 'https://adm.tools/action')
REGISTRAR_API_KEY = _settings.get('REGISTRAR_API_KEY', '')

# Cloudflare API base URL
CLOUDFLARE_API_BASE = 'https://api.cloudflare.com/client/v4'

