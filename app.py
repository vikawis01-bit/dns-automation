from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import json
import os
from config import (
    CLOUDFLARE_API_TOKEN, CLOUDFLARE_EMAIL, CLOUDFLARE_API_KEY,
    CLOUDFLARE_API_BASE, REGISTRAR_API_URL, REGISTRAR_API_KEY, REGISTRAR_API_SECRET
)
from ukraine_registrar import (
    get_ukraine_headers,
    ukraine_get_dns_records,
    ukraine_delete_dns_record,
    ukraine_create_dns_record,
    ukraine_update_nameservers,
    ukraine_update_domain_a_record
)
from ukraine_registrar import (
    ukraine_get_dns_records, ukraine_delete_dns_record, ukraine_create_dns_record,
    ukraine_update_nameservers, get_ukraine_headers
)

app = Flask(__name__)
CORS(app)

def get_cloudflare_headers():
    """Get Cloudflare API headers - использует Global API Key"""
    # Используем Global API Key (Email + API Key)
    return {
        'X-Auth-Email': CLOUDFLARE_EMAIL,
        'X-Auth-Key': CLOUDFLARE_API_KEY,
        'Content-Type': 'application/json'
    }

def get_registrar_headers():
    """Get registrar API headers - использует функции для ukraine.com.ua"""
    return get_ukraine_headers()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stage1', methods=['POST'])
def stage1():
    """Этап 1: Изменение A записей у регистратора"""
    data = request.json
    domains = data.get('domains', [])
    ip_address = data.get('ip_address', '')
    
    if not domains or not ip_address:
        return jsonify({'error': 'Домены и IP адрес обязательны'}), 400
    
    results = []
    
    for domain in domains:
        try:
            # Используем функцию для обновления A записи через API ukraine.com.ua
            ukraine_update_domain_a_record(domain, ip_address)
            
            results.append({
                'domain': domain,
                'status': 'success',
                'message': 'A запись успешно обновлена'
            })
                
        except Exception as e:
            results.append({
                'domain': domain,
                'status': 'error',
                'message': str(e)
            })
    
    return jsonify({'results': results})

@app.route('/api/stage2', methods=['POST'])
def stage2():
    """Этап 2: Добавление доменов в Cloudflare с импортом A записей"""
    data = request.json
    domains = data.get('domains', [])
    
    if not domains:
        return jsonify({'error': 'Домены обязательны'}), 400
    
    results = []
    headers = get_cloudflare_headers()
    
    for domain in domains:
        try:
            # Проверяем, существует ли домен уже в Cloudflare
            zones_url = f"{CLOUDFLARE_API_BASE}/zones?name={domain}"
            zones_response = requests.get(zones_url, headers=headers)
            
            zone_id = None
            if zones_response.status_code == 200:
                zones = zones_response.json()['result']
                if zones:
                    zone_id = zones[0]['id']
            
            # Если домен не существует, добавляем его
            if not zone_id:
                add_domain_url = f"{CLOUDFLARE_API_BASE}/zones"
                zone_data = {
                    'name': domain,
                    'jump_start': True  # Импортирует DNS записи автоматически
                }
                
                response = requests.post(add_domain_url, headers=headers, json=zone_data)
                
                if response.status_code == 200:
                    zone_info = response.json()
                    zone_id = zone_info['result']['id']
                else:
                    error_data = response.json()
                    error_msg = error_data.get('errors', [{}])[0].get('message', 'Неизвестная ошибка')
                    results.append({
                        'domain': domain,
                        'status': 'error',
                        'message': f'Ошибка добавления домена: {error_msg}'
                    })
                    continue
            
            if zone_id:
                # Получаем все записи и оставляем только A записи
                records_url = f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/dns_records"
                records_response = requests.get(records_url, headers=headers)
                
                if records_response.status_code == 200:
                    all_records = records_response.json()['result']
                    
                    # Удаляем все записи кроме A
                    for record in all_records:
                        if record['type'] != 'A':
                            delete_url = f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/dns_records/{record['id']}"
                            requests.delete(delete_url, headers=headers)
                
                results.append({
                    'domain': domain,
                    'status': 'success',
                    'zone_id': zone_id,
                    'message': 'Домен настроен в Cloudflare, оставлены только A записи'
                })
                
        except Exception as e:
            results.append({
                'domain': domain,
                'status': 'error',
                'message': str(e)
            })
    
    return jsonify({'results': results})

@app.route('/api/stage3', methods=['POST'])
def stage3():
    """Этап 3: Получение NS из Cloudflare и обновление у регистратора"""
    data = request.json
    domains = data.get('domains', [])
    
    if not domains:
        return jsonify({'error': 'Домены обязательны'}), 400
    
    results = []
    headers = get_cloudflare_headers()
    
    for domain in domains:
        try:
            # Получаем zone_id домена
            zones_url = f"{CLOUDFLARE_API_BASE}/zones?name={domain}"
            zones_response = requests.get(zones_url, headers=headers)
            
            if zones_response.status_code != 200:
                results.append({
                    'domain': domain,
                    'status': 'error',
                    'message': 'Домен не найден в Cloudflare'
                })
                continue
            
            zones = zones_response.json()['result']
            if not zones:
                results.append({
                    'domain': domain,
                    'status': 'error',
                    'message': 'Домен не найден в Cloudflare'
                })
                continue
            
            zone_id = zones[0]['id']
            
            # Получаем NS записи из Cloudflare
            zone_info_url = f"{CLOUDFLARE_API_BASE}/zones/{zone_id}"
            zone_info_response = requests.get(zone_info_url, headers=headers)
            
            if zone_info_response.status_code == 200:
                zone_info = zone_info_response.json()['result']
                nameservers = zone_info.get('name_servers', [])
                
                if not nameservers:
                    results.append({
                        'domain': domain,
                        'status': 'error',
                        'message': 'NS записи не найдены в Cloudflare'
                    })
                    continue
                
                # Обновляем NS записи у регистратора через API ukraine.com.ua
                ukraine_update_nameservers(domain, nameservers)
                
                results.append({
                    'domain': domain,
                    'status': 'success',
                    'nameservers': nameservers,
                    'message': 'NS записи успешно обновлены'
                })
            else:
                results.append({
                    'domain': domain,
                    'status': 'error',
                    'message': 'Ошибка получения информации о зоне'
                })
                
        except Exception as e:
            results.append({
                'domain': domain,
                'status': 'error',
                'message': str(e)
            })
    
    return jsonify({'results': results})

@app.route('/api/stage4', methods=['POST'])
def stage4():
    """Этап 4: Настройка TLS и Always HTTPS в Cloudflare"""
    data = request.json
    domains = data.get('domains', [])
    
    if not domains:
        return jsonify({'error': 'Домены обязательны'}), 400
    
    results = []
    headers = get_cloudflare_headers()
    
    for domain in domains:
        try:
            # Получаем zone_id домена
            zones_url = f"{CLOUDFLARE_API_BASE}/zones?name={domain}"
            zones_response = requests.get(zones_url, headers=headers)
            
            if zones_response.status_code != 200:
                results.append({
                    'domain': domain,
                    'status': 'error',
                    'message': 'Домен не найден в Cloudflare'
                })
                continue
            
            zones = zones_response.json()['result']
            if not zones:
                results.append({
                    'domain': domain,
                    'status': 'error',
                    'message': 'Домен не найден в Cloudflare'
                })
                continue
            
            zone_id = zones[0]['id']
            
            # Настраиваем TLS минимум 1.2
            ssl_settings_url = f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/settings/ssl"
            ssl_data = {
                'value': 'strict'  # strict использует TLS 1.2+
            }
            ssl_response = requests.patch(ssl_settings_url, headers=headers, json=ssl_data)
            
            # Включаем Always HTTPS
            always_https_url = f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/settings/always_use_https"
            always_https_data = {
                'value': 'on'
            }
            always_https_response = requests.patch(always_https_url, headers=headers, json=always_https_data)
            
            if ssl_response.status_code == 200 and always_https_response.status_code == 200:
                results.append({
                    'domain': domain,
                    'status': 'success',
                    'message': 'TLS и Always HTTPS успешно настроены'
                })
            else:
                ssl_error = ssl_response.json().get('errors', [{}])[0].get('message', '') if ssl_response.status_code != 200 else ''
                https_error = always_https_response.json().get('errors', [{}])[0].get('message', '') if always_https_response.status_code != 200 else ''
                results.append({
                    'domain': domain,
                    'status': 'error',
                    'message': f'Ошибки: SSL: {ssl_error}, Always HTTPS: {https_error}'
                })
                
        except Exception as e:
            results.append({
                'domain': domain,
                'status': 'error',
                'message': str(e)
            })
    
    return jsonify({'results': results})

@app.route('/api/run-all', methods=['POST'])
def run_all():
    """Запуск всех этапов последовательно"""
    data = request.json
    domains = data.get('domains', [])
    ip_address = data.get('ip_address', '')
    
    if not domains or not ip_address:
        return jsonify({'error': 'Домены и IP адрес обязательны'}), 400
    
    all_results = {
        'stage1': None,
        'stage2': None,
        'stage3': None,
        'stage4': None
    }
    
    # Этап 1
    stage1_data = {'domains': domains, 'ip_address': ip_address}
    stage1_result = stage1()
    all_results['stage1'] = stage1_result.get_json()
    
    # Этап 2
    stage2_data = {'domains': domains}
    stage2_result = stage2()
    all_results['stage2'] = stage2_result.get_json()
    
    # Этап 3
    stage3_data = {'domains': domains}
    stage3_result = stage3()
    all_results['stage3'] = stage3_result.get_json()
    
    # Этап 4
    stage4_data = {'domains': domains}
    stage4_result = stage4()
    all_results['stage4'] = stage4_result.get_json()
    
    return jsonify(all_results)

def check_config():
    """Проверка конфигурации при запуске"""
    warnings = []
    
    if not CLOUDFLARE_EMAIL or not CLOUDFLARE_API_KEY:
        warnings.append("⚠️  Cloudflare API credentials не настроены! (нужны CLOUDFLARE_EMAIL и CLOUDFLARE_API_KEY)")
    
    if not REGISTRAR_API_URL or not REGISTRAR_API_KEY:
        warnings.append("⚠️  Ukraine.com.ua API credentials не настроены! (нужны REGISTRAR_API_URL и REGISTRAR_API_KEY)")
    
    if warnings:
        print("\n".join(warnings))
        print("\nПожалуйста, настройте .env файл перед использованием.\n")
    else:
        print("✓ Конфигурация загружена успешно")

if __name__ == '__main__':
    check_config()
    # Для продакшена используйте переменную окружения PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

