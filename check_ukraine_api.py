"""
Временный скрипт для проверки правильного URL API ukraine.com.ua
Используйте этот скрипт для тестирования разных вариантов URL
"""

import requests

# Варианты URL для проверки
API_URLS = [
    "https://www.ukraine.com.ua/api/v2",
    "https://api.ukraine.com.ua/v2",
    "https://ukraine.com.ua/api/v2",
    "https://www.ukraine.com.ua/api",
    "https://api.ukraine.com.ua",
]

# Ваш API ключ (замените на реальный)
API_KEY = "ваш_api_ключ"

def test_api_url(base_url, api_key):
    """Тестирование URL API"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Пробуем разные endpoints
    endpoints = [
        f"{base_url}/domains",
        f"{base_url}/domains/test.com/dns",
        f"{base_url}/domains/test.com",
    ]
    
    print(f"\n🔍 Тестирую: {base_url}")
    print("-" * 60)
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"  {endpoint}")
            print(f"    Status: {response.status_code}")
            if response.status_code != 404:
                print(f"    Response: {response.text[:200]}")
        except requests.exceptions.RequestException as e:
            print(f"  {endpoint}")
            print(f"    Error: {str(e)[:100]}")

if __name__ == "__main__":
    print("🔍 Проверка правильного URL API ukraine.com.ua")
    print("=" * 60)
    
    if API_KEY == "ваш_api_ключ":
        print("⚠️  Замените API_KEY на ваш реальный ключ!")
        print("\nИли запустите из веб-интерфейса - там будет автоматическая проверка.")
    else:
        for url in API_URLS:
            test_api_url(url, API_KEY)

