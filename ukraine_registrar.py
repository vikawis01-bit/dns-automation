"""
Модуль для работы с API регистратора ukraine.com.ua

Официальные ресурсы:
- GitHub: https://github.com/ukraine-com-ua/API
- Документация: https://www.ukraine.com.ua/ru/wiki/account/api/
- Документация в панели: Раздел "API" → "Документация"

ВАЖНО:
1. Токен нужно активировать в панели управления (раздел "API" → "Данные доступа")
2. Токен действует 6 месяцев с момента последнего использования
3. Рекомендуется настроить ограничение доступа по IP
4. Лимиты: 300 запросов/час, 5000/сутки

Если возникают ошибки, проверьте:
- Правильность URL API (может отличаться, проверьте в панели)
- Формат ответов API (JSON структура)
- Названия полей (id, record_id, _id и т.д.)
- Формат данных для создания/обновления записей
- Схему аутентификации (Bearer Token, X-API-Key и т.д.)
"""

import requests
from config import REGISTRAR_API_URL, REGISTRAR_API_KEY

def get_ukraine_headers(api_keys=None):
    """
    Получение заголовков для API ukraine.com.ua
    
    Согласно документации: https://www.ukraine.com.ua/ru/wiki/account/api/
    API использует токен, который нужно активировать в панели управления.
    Токен действует 6 месяцев с момента последнего использования.
    
    Возможные форматы авторизации:
    - Bearer Token (Authorization: Bearer {token})
    - API Key в заголовке (X-API-Key: {key})
    """
    # Если переданы ключи из запроса, используем их, иначе из конфига
    if api_keys:
        api_key = api_keys.get('registrar_api_key', '')
    else:
        api_key = REGISTRAR_API_KEY
    
    # Пробуем разные варианты авторизации
    # Сначала Bearer Token (стандартный)
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Также добавляем X-API-Key на случай если используется такой формат
    headers['X-API-Key'] = api_key
    
    return headers

def ukraine_get_dns_records(domain, api_keys=None):
    """
    Получение DNS записей домена через API ukraine.com.ua
    
    API endpoint: GET /domains/{domain}/dns
    
    Возможные варианты URL:
    - https://www.ukraine.com.ua/api/v2
    - https://api.ukraine.com.ua/v2
    - https://ukraine.com.ua/api/v2
    """
    api_url = api_keys.get('registrar_api_url', REGISTRAR_API_URL) if api_keys else REGISTRAR_API_URL
    
    # Убираем слэш в конце если есть
    api_url = api_url.rstrip('/')
    
    # Определяем, есть ли уже /v2 или /api/v2 в базовом URL
    has_v2 = '/v2' in api_url or '/api/v2' in api_url
    
    # Пробуем разные варианты endpoints (избегаем дублирования /v2)
    if has_v2:
        # Если в базовом URL уже есть /v2, не добавляем его снова
        endpoints = [
            f"{api_url}/domains/{domain}/dns",
            f"{api_url}/domains/{domain}/dns-records",
        ]
    else:
        # Если в базовом URL нет /v2, пробуем разные варианты
        endpoints = [
            f"{api_url}/domains/{domain}/dns",
            f"{api_url}/api/v2/domains/{domain}/dns",
            f"{api_url}/v2/domains/{domain}/dns",
            f"{api_url}/domains/{domain}/dns-records",
        ]
    
    headers = get_ukraine_headers(api_keys)
    
    last_error = None
    for url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            last_error = e
            continue
    
    # Если все варианты не сработали
    error_msg = str(last_error) if last_error else "Неизвестная ошибка"
    if "Failed to resolve" in error_msg or "Name or service not known" in error_msg:
        raise Exception(f"Не удается подключиться к API ukraine.com.ua. Проверьте правильность URL API. Текущий URL: {api_url}. Ошибка: {error_msg}")
    raise Exception(f"Ошибка получения DNS записей: {error_msg}")

def ukraine_delete_dns_record(domain, record_id, api_keys=None):
    """
    Удаление DNS записи через API ukraine.com.ua
    
    API endpoint: DELETE /domains/{domain}/dns/{record_id}
    """
    api_url = api_keys.get('registrar_api_url', REGISTRAR_API_URL) if api_keys else REGISTRAR_API_URL
    api_url = api_url.rstrip('/')
    
    # Определяем, есть ли уже /v2 или /api/v2 в базовом URL
    has_v2 = '/v2' in api_url or '/api/v2' in api_url
    
    # Пробуем разные варианты endpoints (избегаем дублирования /v2)
    if has_v2:
        endpoints = [
            f"{api_url}/domains/{domain}/dns/{record_id}",
        ]
    else:
        endpoints = [
            f"{api_url}/domains/{domain}/dns/{record_id}",
            f"{api_url}/api/v2/domains/{domain}/dns/{record_id}",
            f"{api_url}/v2/domains/{domain}/dns/{record_id}",
        ]
    
    headers = get_ukraine_headers(api_keys)
    
    for url in endpoints:
        try:
            response = requests.delete(url, headers=headers, timeout=30)
            if response.status_code in [200, 204, 404]:
                return True
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            continue
    
    # Игнорируем ошибки удаления, если запись уже не существует
    return False

def ukraine_create_dns_record(domain, record_type, name, content, ttl=3600, api_keys=None):
    """
    Создание DNS записи через API ukraine.com.ua
    
    API endpoint: POST /domains/{domain}/dns
    
    Args:
        domain: доменное имя
        record_type: тип записи (A, AAAA, CNAME, MX, TXT и т.д.)
        name: имя записи (@ для корня домена)
        content: содержимое записи (IP для A записи)
        ttl: время жизни записи в секундах
        api_keys: словарь с API ключами (опционально)
    """
    api_url = api_keys.get('registrar_api_url', REGISTRAR_API_URL) if api_keys else REGISTRAR_API_URL
    api_url = api_url.rstrip('/')
    
    # Определяем, есть ли уже /v2 или /api/v2 в базовом URL
    has_v2 = '/v2' in api_url or '/api/v2' in api_url
    
    # Пробуем разные варианты endpoints (избегаем дублирования /v2)
    if has_v2:
        endpoints = [
            f"{api_url}/domains/{domain}/dns",
        ]
    else:
        endpoints = [
            f"{api_url}/domains/{domain}/dns",
            f"{api_url}/api/v2/domains/{domain}/dns",
            f"{api_url}/v2/domains/{domain}/dns",
        ]
    
    headers = get_ukraine_headers(api_keys)
    
    data = {
        'type': record_type,
        'name': name,
        'content': content,
        'ttl': ttl
    }
    
    last_error = None
    for url in endpoints:
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            last_error = e
            continue
    
    error_msg = str(last_error) if last_error else "Неизвестная ошибка"
    if "Failed to resolve" in error_msg or "Name or service not known" in error_msg:
        raise Exception(f"Не удается подключиться к API ukraine.com.ua. Проверьте правильность URL API. Текущий URL: {api_url}. Ошибка: {error_msg}")
    raise Exception(f"Ошибка создания DNS записи: {error_msg}")

def ukraine_update_nameservers(domain, nameservers, api_keys=None):
    """
    Обновление NS записей через API ukraine.com.ua
    
    API endpoint: PUT /domains/{domain}/nameservers
    
    Args:
        domain: доменное имя
        nameservers: список nameservers от Cloudflare
        api_keys: словарь с API ключами (опционально)
    """
    api_url = api_keys.get('registrar_api_url', REGISTRAR_API_URL) if api_keys else REGISTRAR_API_URL
    api_url = api_url.rstrip('/')
    
    # Пробуем разные варианты endpoints
    endpoints = [
        f"{api_url}/domains/{domain}/nameservers",
        f"{api_url}/api/v2/domains/{domain}/nameservers",
        f"{api_url}/v2/domains/{domain}/nameservers",
    ]
    
    headers = get_ukraine_headers(api_keys)
    
    # Формат может отличаться в зависимости от API
    data_variants = [
        {'nameservers': nameservers},  # Вариант 1
        {'ns': nameservers},  # Вариант 2
        {'name_servers': nameservers}  # Вариант 3
    ]
    
    last_error = None
    for endpoint_url in endpoints:
        for data in data_variants:
            try:
                response = requests.put(endpoint_url, headers=headers, json=data, timeout=30)
                if response.status_code in [200, 201, 204]:
                    return response.json() if response.content else {'status': 'success'}
            except requests.exceptions.RequestException as e:
                last_error = e
                continue
        
        # Если все варианты данных не сработали, попробуем как список
        try:
            response = requests.put(endpoint_url, headers=headers, json=nameservers, timeout=30)
            if response.status_code in [200, 201, 204]:
                return response.json() if response.content else {'status': 'success'}
        except requests.exceptions.RequestException as e:
            last_error = e
            continue
    
    error_msg = str(last_error) if last_error else "Неизвестная ошибка"
    if "Failed to resolve" in error_msg or "Name or service not known" in error_msg:
        raise Exception(f"Не удается подключиться к API ukraine.com.ua. Проверьте правильность URL API. Текущий URL: {api_url}. Ошибка: {error_msg}")
    raise Exception(f"Ошибка обновления NS записей: {error_msg}")

def ukraine_update_domain_a_record(domain, ip_address, api_keys=None):
    """
    Обновление A записи домена: удаление всех записей и создание новой A записи
    
    Args:
        domain: доменное имя
        ip_address: IP адрес для A записи
        api_keys: словарь с API ключами (опционально)
    """
    try:
        # Получаем все DNS записи
        records_data = ukraine_get_dns_records(domain, api_keys)
        
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
                ukraine_delete_dns_record(domain, record_id, api_keys)
        
        # Создаем новую A запись
        result = ukraine_create_dns_record(domain, 'A', '@', ip_address, 3600, api_keys)
        return {'status': 'success', 'message': 'A запись успешно обновлена'}
        
    except Exception as e:
        raise Exception(f"Ошибка обновления A записи: {str(e)}")
