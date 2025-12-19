"""
Примеры интеграции с API различных регистраторов
Используйте эти примеры для адаптации функций в app.py под ваш регистратор
"""

import requests
from config import REGISTRAR_API_URL, REGISTRAR_API_KEY, REGISTRAR_API_SECRET

# ============================================
# Пример 1: Namecheap API
# ============================================
def namecheap_get_dns_records(domain):
    """Получение DNS записей через Namecheap API"""
    url = f"{REGISTRAR_API_URL}/domains.dns.getHosts"
    params = {
        'ApiUser': REGISTRAR_API_KEY,
        'ApiKey': REGISTRAR_API_SECRET,
        'UserName': REGISTRAR_API_KEY,
        'Command': 'namecheap.domains.dns.getHosts',
        'ClientIp': '127.0.0.1',
        'SLD': domain.split('.')[0],
        'TLD': '.'.join(domain.split('.')[1:])
    }
    response = requests.get(url, params=params)
    return response.json()

def namecheap_set_dns_records(domain, ip_address):
    """Установка A записи через Namecheap API"""
    url = f"{REGISTRAR_API_URL}/domains.dns.setHosts"
    params = {
        'ApiUser': REGISTRAR_API_KEY,
        'ApiKey': REGISTRAR_API_SECRET,
        'UserName': REGISTRAR_API_KEY,
        'Command': 'namecheap.domains.dns.setHosts',
        'ClientIp': '127.0.0.1',
        'SLD': domain.split('.')[0],
        'TLD': '.'.join(domain.split('.')[1:]),
        'HostName1': '@',
        'RecordType1': 'A',
        'Address1': ip_address,
        'TTL1': '3600'
    }
    response = requests.post(url, params=params)
    return response.json()

# ============================================
# Пример 2: GoDaddy API
# ============================================
def godaddy_get_dns_records(domain):
    """Получение DNS записей через GoDaddy API"""
    url = f"{REGISTRAR_API_URL}/v1/domains/{domain}/records"
    headers = {
        'Authorization': f'sso-key {REGISTRAR_API_KEY}:{REGISTRAR_API_SECRET}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def godaddy_update_dns_records(domain, ip_address):
    """Обновление A записи через GoDaddy API"""
    url = f"{REGISTRAR_API_URL}/v1/domains/{domain}/records/A/@"
    headers = {
        'Authorization': f'sso-key {REGISTRAR_API_KEY}:{REGISTRAR_API_SECRET}',
        'Content-Type': 'application/json'
    }
    data = [{
        'data': ip_address,
        'ttl': 3600
    }]
    response = requests.put(url, headers=headers, json=data)
    return response.json()

def godaddy_delete_dns_records(domain, record_type):
    """Удаление DNS записей через GoDaddy API"""
    url = f"{REGISTRAR_API_URL}/v1/domains/{domain}/records/{record_type}"
    headers = {
        'Authorization': f'sso-key {REGISTRAR_API_KEY}:{REGISTRAR_API_SECRET}'
    }
    response = requests.delete(url, headers=headers)
    return response.status_code == 204

# ============================================
# Пример 3: Name.com API
# ============================================
def namecom_get_dns_records(domain):
    """Получение DNS записей через Name.com API"""
    url = f"{REGISTRAR_API_URL}/v4/domains/{domain}/records"
    headers = {
        'Authorization': f'Basic {REGISTRAR_API_KEY}:{REGISTRAR_API_SECRET}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def namecom_update_dns_records(domain, ip_address):
    """Обновление DNS записей через Name.com API"""
    # Сначала получаем все записи
    records = namecom_get_dns_records(domain)
    
    # Удаляем все записи кроме нужных
    url = f"{REGISTRAR_API_URL}/v4/domains/{domain}/records"
    headers = {
        'Authorization': f'Basic {REGISTRAR_API_KEY}:{REGISTRAR_API_SECRET}',
        'Content-Type': 'application/json'
    }
    
    # Удаляем все существующие записи
    for record in records.get('records', []):
        delete_url = f"{REGISTRAR_API_URL}/v4/domains/{domain}/records/{record['id']}"
        requests.delete(delete_url, headers=headers)
    
    # Создаем новую A запись
    data = {
        'host': '@',
        'type': 'A',
        'answer': ip_address,
        'ttl': 3600
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# ============================================
# Пример 4: Generic REST API (универсальный)
# ============================================
def generic_get_dns_records(domain):
    """Универсальная функция для получения DNS записей"""
    url = f"{REGISTRAR_API_URL}/domains/{domain}/dns"
    headers = {
        'Authorization': f'Bearer {REGISTRAR_API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def generic_update_nameservers(domain, nameservers):
    """Универсальная функция для обновления NS записей"""
    url = f"{REGISTRAR_API_URL}/domains/{domain}/nameservers"
    headers = {
        'Authorization': f'Bearer {REGISTRAR_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'nameservers': nameservers
    }
    response = requests.put(url, headers=headers, json=data)
    return response.json()

