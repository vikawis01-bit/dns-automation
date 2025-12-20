"""
Модуль для работы с API регистратора ukraine.com.ua

Официальные ресурсы:
- GitHub: https://github.com/ukraine-com-ua/API
- Документация: https://www.ukraine.com.ua/ru/wiki/account/api/
- Базовый URL API: https://adm.tools/action/

ВАЖНО:
1. Токен нужно активировать в панели управления (раздел "API" → "Данные доступа")
2. Токен действует 6 месяцев с момента последнего использования
3. Рекомендуется настроить ограничение доступа по IP
4. Лимиты: 300 запросов/час, 5000/сутки

Формат API:
- Базовый URL: https://adm.tools/action/
- Авторизация: Authorization: Bearer {token}
- Метод: POST
- Данные: POST в формате http_build_query, параметры в GET
"""

import requests
from urllib.parse import urlencode
from config import REGISTRAR_API_URL, REGISTRAR_API_KEY

# Базовый URL API ukraine.com.ua
UKRAINE_API_BASE = 'https://adm.tools/action'

def get_ukraine_headers(api_keys=None):
    """
    Получение заголовков для API ukraine.com.ua
    
    Формат: Authorization: Bearer {token}
    """
    # Если переданы ключи из запроса, используем их, иначе из конфига
    if api_keys:
        api_key = api_keys.get('registrar_api_key', '')
    else:
        api_key = REGISTRAR_API_KEY
    
    if not api_key:
        raise Exception("API токен не указан. Заполните настройки API.")
    
    return {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

def get_ukraine_api_base(api_keys=None):
    """Получение базового URL API"""
    if api_keys:
        api_url = api_keys.get('registrar_api_url', UKRAINE_API_BASE)
    else:
        api_url = REGISTRAR_API_URL if REGISTRAR_API_URL else UKRAINE_API_BASE
    
    # Если URL не содержит базовый путь, используем стандартный
    if 'adm.tools' not in api_url:
        api_url = UKRAINE_API_BASE
    
    return api_url.rstrip('/')

def ukraine_get_dns_records(domain, api_keys=None):
    """
    Получение DNS записей домена через API ukraine.com.ua
    
    API endpoint: dns/record_list
    
    Args:
        domain: доменное имя
        api_keys: словарь с API ключами (опционально)
    """
    api_base = get_ukraine_api_base(api_keys)
    url = f"{api_base}/dns/record_list/"
    
    # Параметры GET запроса
    get_params = {
        'domain': domain
    }
    
    url_with_params = f"{url}?{urlencode(get_params)}"
    headers = get_ukraine_headers(api_keys)
    
    # POST данные - для получения списка может быть пустым массивом или пустой строкой
    # Пробуем разные варианты
    post_data_variants = [
        '',  # Пустая строка
        urlencode({}),  # Пустой объект как query string
    ]
    
    last_error = None
    for post_data in post_data_variants:
        try:
            response = requests.post(
                url_with_params,
                headers=headers,
                data=post_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            last_error = e
            # Если 400 ошибка, пробуем следующий вариант
            if '400' in str(e):
                continue
            # Для других ошибок сразу выбрасываем исключение
            raise Exception(f"Ошибка получения DNS записей: {str(e)}")
    
    # Если все варианты не сработали
    error_msg = str(last_error) if last_error else "Неизвестная ошибка"
    raise Exception(f"Ошибка получения DNS записей (400 Bad Request). Проверьте правильность токена и домена. Ошибка: {error_msg}")

def ukraine_delete_dns_record(domain, record_id, api_keys=None):
    """
    Удаление DNS записи через API ukraine.com.ua
    
    API endpoint: dns/record_delete
    
    Args:
        domain: доменное имя
        record_id: ID записи для удаления (subdomain_id)
        api_keys: словарь с API ключами (опционально)
    """
    api_base = get_ukraine_api_base(api_keys)
    url = f"{api_base}/dns/record_delete/"
    
    # Параметры GET запроса
    get_params = {
        'domain': domain
    }
    
    url_with_params = f"{url}?{urlencode(get_params)}"
    headers = get_ukraine_headers(api_keys)
    
    # POST данные
    post_data = {
        'subdomain_id': record_id
    }
    
    try:
        response = requests.post(
            url_with_params,
            headers=headers,
            data=urlencode(post_data),
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        # Проверяем успешность операции
        if result.get('status') == 'success' or response.status_code == 200:
            return True
        return False
    except requests.exceptions.RequestException:
        # Игнорируем ошибки удаления, если запись уже не существует
        return False

def ukraine_create_dns_record(domain, record_type, name, content, ttl=3600, api_keys=None):
    """
    Создание DNS записи через API ukraine.com.ua
    
    API endpoint: dns/record_add
    
    Args:
        domain: доменное имя
        record_type: тип записи (A, AAAA, CNAME, MX, TXT и т.д.)
        name: имя записи (@ для корня домена, или поддомен)
        content: содержимое записи (IP для A записи)
        ttl: время жизни записи в секундах
        api_keys: словарь с API ключами (опционально)
    """
    api_base = get_ukraine_api_base(api_keys)
    url = f"{api_base}/dns/record_add/"
    
    # Параметры GET запроса
    get_params = {
        'domain': domain
    }
    
    url_with_params = f"{url}?{urlencode(get_params)}"
    headers = get_ukraine_headers(api_keys)
    
    # POST данные
    post_data = {
        'type': record_type,
        'subdomain': name if name != '@' else '',  # @ означает корень домена
        'data': content,
        'ttl': ttl,
        'priority': 0  # Для MX записей
    }
    
    try:
        response = requests.post(
            url_with_params,
            headers=headers,
            data=urlencode(post_data),
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка создания DNS записи: {str(e)}")

def ukraine_update_dns_record(domain, record_id, record_type, name, content, ttl=3600, api_keys=None):
    """
    Обновление DNS записи через API ukraine.com.ua
    
    API endpoint: dns/record_edit
    
    Args:
        domain: доменное имя
        record_id: ID записи (subdomain_id)
        record_type: тип записи
        name: имя записи
        content: содержимое записи
        ttl: время жизни записи
        api_keys: словарь с API ключами (опционально)
    """
    api_base = get_ukraine_api_base(api_keys)
    url = f"{api_base}/dns/record_edit/"
    
    # Параметры GET запроса
    get_params = {
        'domain': domain
    }
    
    url_with_params = f"{url}?{urlencode(get_params)}"
    headers = get_ukraine_headers(api_keys)
    
    # POST данные
    post_data = {
        'subdomain_id': record_id,
        'type': record_type,
        'subdomain': name if name != '@' else '',
        'data': content,
        'ttl': ttl,
        'priority': 0
    }
    
    try:
        response = requests.post(
            url_with_params,
            headers=headers,
            data=urlencode(post_data),
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка обновления DNS записи: {str(e)}")

def ukraine_update_nameservers(domain, nameservers, api_keys=None):
    """
    Обновление NS записей через API ukraine.com.ua
    
    API endpoint: dns/nameservers_set или domain/nameservers_set
    
    Args:
        domain: доменное имя
        nameservers: список nameservers от Cloudflare
        api_keys: словарь с API ключами (опционально)
    """
    api_base = get_ukraine_api_base(api_keys)
    
    # Пробуем разные варианты endpoints
    endpoints = [
        f"{api_base}/dns/nameservers_set/",
        f"{api_base}/domain/nameservers_set/",
    ]
    
    headers = get_ukraine_headers(api_keys)
    
    # Параметры GET запроса
    get_params = {
        'domain': domain
    }
    
    # POST данные - пробуем разные форматы
    data_variants = [
        {'nameservers': ','.join(nameservers)},
        {'nameservers': nameservers},
        {'ns': ','.join(nameservers)},
        {'ns': nameservers},
    ]
    
    last_error = None
    for endpoint_url in endpoints:
        url_with_params = f"{endpoint_url}?{urlencode(get_params)}"
        
        for post_data in data_variants:
            try:
                response = requests.post(
                    url_with_params,
                    headers=headers,
                    data=urlencode(post_data) if isinstance(post_data.get(list(post_data.keys())[0]), str) else urlencode({k: ','.join(v) if isinstance(v, list) else v for k, v in post_data.items()}),
                    timeout=30
                )
                if response.status_code in [200, 201]:
                    result = response.json()
                    if result.get('status') == 'success' or 'success' in str(result).lower():
                        return result
            except requests.exceptions.RequestException as e:
                last_error = e
                continue
    
    error_msg = str(last_error) if last_error else "Неизвестная ошибка"
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
            # Пробуем разные варианты структуры ответа
            records = records_data.get('result', records_data.get('data', records_data.get('records', [])))
            if isinstance(records, dict):
                records = records.get('list', [])
        elif isinstance(records_data, list):
            records = records_data
        
        # Удаляем все существующие записи
        for record in records:
            record_id = None
            if isinstance(record, dict):
                record_id = record.get('subdomain_id', record.get('id', record.get('record_id', record.get('_id'))))
            elif isinstance(record, str):
                record_id = record
            
            if record_id:
                ukraine_delete_dns_record(domain, record_id, api_keys)
        
        # Создаем новую A запись для корня домена
        result = ukraine_create_dns_record(domain, 'A', '@', ip_address, 3600, api_keys)
        return {'status': 'success', 'message': 'A запись успешно обновлена'}
        
    except Exception as e:
        raise Exception(f"Ошибка обновления A записи: {str(e)}")
