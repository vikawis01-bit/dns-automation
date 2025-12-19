"""
Модуль для работы с API регистратора ukraine.com.ua
API v2: https://www.ukraine.com.ua/domains/apiv2/

ВАЖНО: Структура API может отличаться от ожидаемой.
Если возникают ошибки, проверьте документацию API и адаптируйте функции:
- Формат ответов API (JSON структура)
- Названия полей (id, record_id, _id и т.д.)
- Формат данных для создания/обновления записей
- Схему аутентификации (Basic Auth, Bearer Token и т.д.)
"""

import requests
from config import REGISTRAR_API_URL, REGISTRAR_API_KEY, REGISTRAR_API_SECRET

def get_ukraine_headers():
    """Получение заголовков для API ukraine.com.ua"""
    # API ukraine.com.ua обычно использует Basic Auth или Token
    # Адаптируйте под вашу схему аутентификации
    if REGISTRAR_API_SECRET:
        # Basic Auth
        import base64
        credentials = f"{REGISTRAR_API_KEY}:{REGISTRAR_API_SECRET}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {
            'Authorization': f'Basic {encoded}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    else:
        # Token Auth
        return {
            'Authorization': f'Bearer {REGISTRAR_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

def ukraine_get_dns_records(domain):
    """
    Получение DNS записей домена через API ukraine.com.ua
    
    API endpoint: GET /domains/{domain}/dns
    """
    url = f"{REGISTRAR_API_URL}/domains/{domain}/dns"
    headers = get_ukraine_headers()
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка получения DNS записей: {str(e)}")

def ukraine_delete_dns_record(domain, record_id):
    """
    Удаление DNS записи через API ukraine.com.ua
    
    API endpoint: DELETE /domains/{domain}/dns/{record_id}
    """
    url = f"{REGISTRAR_API_URL}/domains/{domain}/dns/{record_id}"
    headers = get_ukraine_headers()
    
    try:
        response = requests.delete(url, headers=headers, timeout=30)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        # Игнорируем ошибки удаления, если запись уже не существует
        return False

def ukraine_create_dns_record(domain, record_type, name, content, ttl=3600):
    """
    Создание DNS записи через API ukraine.com.ua
    
    API endpoint: POST /domains/{domain}/dns
    
    Args:
        domain: доменное имя
        record_type: тип записи (A, AAAA, CNAME, MX, TXT и т.д.)
        name: имя записи (@ для корня домена)
        content: содержимое записи (IP для A записи)
        ttl: время жизни записи в секундах
    """
    url = f"{REGISTRAR_API_URL}/domains/{domain}/dns"
    headers = get_ukraine_headers()
    
    data = {
        'type': record_type,
        'name': name,
        'content': content,
        'ttl': ttl
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка создания DNS записи: {str(e)}")

def ukraine_update_nameservers(domain, nameservers):
    """
    Обновление NS записей через API ukraine.com.ua
    
    API endpoint: PUT /domains/{domain}/nameservers
    
    Args:
        domain: доменное имя
        nameservers: список nameservers от Cloudflare
    """
    url = f"{REGISTRAR_API_URL}/domains/{domain}/nameservers"
    headers = get_ukraine_headers()
    
    # Формат может отличаться в зависимости от API
    # Попробуем оба варианта
    data_variants = [
        {'nameservers': nameservers},  # Вариант 1
        {'ns': nameservers},  # Вариант 2
        {'name_servers': nameservers}  # Вариант 3
    ]
    
    for data in data_variants:
        try:
            response = requests.put(url, headers=headers, json=data, timeout=30)
            if response.status_code in [200, 201, 204]:
                return response.json() if response.content else {'status': 'success'}
        except requests.exceptions.RequestException:
            continue
    
    # Если все варианты не сработали, попробуем как список
    try:
        response = requests.put(url, headers=headers, json=nameservers, timeout=30)
        response.raise_for_status()
        return response.json() if response.content else {'status': 'success'}
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка обновления NS записей: {str(e)}")

def ukraine_update_domain_a_record(domain, ip_address):
    """
    Обновление A записи домена: удаление всех записей и создание новой A записи
    
    Args:
        domain: доменное имя
        ip_address: IP адрес для A записи
    """
    try:
        # Получаем все DNS записи
        records_data = ukraine_get_dns_records(domain)
        
        # Извлекаем список записей (структура может отличаться)
        records = []
        if isinstance(records_data, dict):
            records = records_data.get('records', records_data.get('data', records_data.get('dns_records', [])))
        elif isinstance(records_data, list):
            records = records_data
        
        # Удаляем все существующие записи
        for record in records:
            record_id = None
            if isinstance(record, dict):
                record_id = record.get('id', record.get('record_id', record.get('_id')))
            elif isinstance(record, str):
                record_id = record
            
            if record_id:
                ukraine_delete_dns_record(domain, record_id)
        
        # Создаем новую A запись
        result = ukraine_create_dns_record(domain, 'A', '@', ip_address, 3600)
        return {'status': 'success', 'message': 'A запись успешно обновлена'}
        
    except Exception as e:
        raise Exception(f"Ошибка обновления A записи: {str(e)}")
