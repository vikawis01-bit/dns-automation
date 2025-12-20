"""
Модуль для работы с API регистратора Namecheap
Документация: https://www.namecheap.com/support/api/
"""

import requests
from config import REGISTRAR_API_URL, REGISTRAR_API_KEY, REGISTRAR_API_SECRET

def get_namecheap_headers():
    """Получение заголовков для API Namecheap"""
    # Namecheap использует параметры запроса, а не заголовки
    return {}

def namecheap_get_dns_records(domain, api_keys=None):
    """
    Получение DNS записей через Namecheap API
    
    API endpoint: domains.dns.getHosts
    
    Args:
        domain: доменное имя (например, example.com)
        api_keys: словарь с ключами (ApiUser, ApiKey, UserName, ClientIp)
    """
    # Namecheap API URL
    api_url = api_keys.get('registrar_api_url', REGISTRAR_API_URL) if api_keys else REGISTRAR_API_URL
    if not api_url:
        api_url = 'https://api.namecheap.com/xml.response'  # По умолчанию
    
    # Получаем ключи
    if api_keys:
        api_user = api_keys.get('registrar_api_user', api_keys.get('registrar_api_key', ''))
        api_key = api_keys.get('registrar_api_secret', api_keys.get('registrar_api_key', ''))
        user_name = api_keys.get('registrar_user_name', api_user)
        client_ip = api_keys.get('registrar_client_ip', '127.0.0.1')
    else:
        api_user = REGISTRAR_API_KEY
        api_key = REGISTRAR_API_SECRET
        user_name = api_user
        client_ip = '127.0.0.1'
    
    # Разделяем домен на SLD и TLD
    parts = domain.split('.')
    sld = parts[0]
    tld = '.'.join(parts[1:])
    
    params = {
        'ApiUser': api_user,
        'ApiKey': api_key,
        'UserName': user_name,
        'Command': 'namecheap.domains.dns.getHosts',
        'ClientIp': client_ip,
        'SLD': sld,
        'TLD': tld
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        # Namecheap возвращает XML, нужно парсить
        return response.text  # Или используйте xml.etree.ElementTree для парсинга
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка получения DNS записей: {str(e)}")

def namecheap_set_dns_records(domain, ip_address, api_keys=None):
    """
    Установка A записи через Namecheap API
    
    API endpoint: domains.dns.setHosts
    
    Args:
        domain: доменное имя
        ip_address: IP адрес для A записи
        api_keys: словарь с ключами
    """
    api_url = api_keys.get('registrar_api_url', REGISTRAR_API_URL) if api_keys else REGISTRAR_API_URL
    if not api_url:
        api_url = 'https://api.namecheap.com/xml.response'
    
    if api_keys:
        api_user = api_keys.get('registrar_api_user', api_keys.get('registrar_api_key', ''))
        api_key = api_keys.get('registrar_api_secret', api_keys.get('registrar_api_key', ''))
        user_name = api_keys.get('registrar_user_name', api_user)
        client_ip = api_keys.get('registrar_client_ip', '127.0.0.1')
    else:
        api_user = REGISTRAR_API_KEY
        api_key = REGISTRAR_API_SECRET
        user_name = api_user
        client_ip = '127.0.0.1'
    
    parts = domain.split('.')
    sld = parts[0]
    tld = '.'.join(parts[1:])
    
    params = {
        'ApiUser': api_user,
        'ApiKey': api_key,
        'UserName': user_name,
        'Command': 'namecheap.domains.dns.setHosts',
        'ClientIp': client_ip,
        'SLD': sld,
        'TLD': tld,
        'HostName1': '@',
        'RecordType1': 'A',
        'Address1': ip_address,
        'TTL1': '3600'
    }
    
    try:
        response = requests.post(api_url, params=params, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка установки DNS записей: {str(e)}")

def namecheap_update_domain_a_record(domain, ip_address, api_keys=None):
    """
    Обновление A записи домена через Namecheap API
    Удаляет все записи и создает новую A запись
    
    Args:
        domain: доменное имя
        ip_address: IP адрес для A записи
        api_keys: словарь с ключами
    """
    try:
        # Namecheap setHosts заменяет все записи, так что просто вызываем set
        return namecheap_set_dns_records(domain, ip_address, api_keys)
    except Exception as e:
        raise Exception(f"Ошибка обновления A записи: {str(e)}")

def namecheap_update_nameservers(domain, nameservers, api_keys=None):
    """
    Обновление NS записей через Namecheap API
    
    API endpoint: domains.dns.setCustom
    
    Args:
        domain: доменное имя
        nameservers: список nameservers от Cloudflare
        api_keys: словарь с ключами
    """
    api_url = api_keys.get('registrar_api_url', REGISTRAR_API_URL) if api_keys else REGISTRAR_API_URL
    if not api_url:
        api_url = 'https://api.namecheap.com/xml.response'
    
    if api_keys:
        api_user = api_keys.get('registrar_api_user', api_keys.get('registrar_api_key', ''))
        api_key = api_keys.get('registrar_api_secret', api_keys.get('registrar_api_key', ''))
        user_name = api_keys.get('registrar_user_name', api_user)
        client_ip = api_keys.get('registrar_client_ip', '127.0.0.1')
    else:
        api_user = REGISTRAR_API_KEY
        api_key = REGISTRAR_API_SECRET
        user_name = api_user
        client_ip = '127.0.0.1'
    
    parts = domain.split('.')
    sld = parts[0]
    tld = '.'.join(parts[1:])
    
    # Формируем параметры для NS записей
    params = {
        'ApiUser': api_user,
        'ApiKey': api_key,
        'UserName': user_name,
        'Command': 'namecheap.domains.dns.setCustom',
        'ClientIp': client_ip,
        'SLD': sld,
        'TLD': tld,
    }
    
    # Добавляем nameservers
    for i, ns in enumerate(nameservers, 1):
        params[f'Nameserver{i}'] = ns
    
    try:
        response = requests.post(api_url, params=params, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка обновления NS записей: {str(e)}")

