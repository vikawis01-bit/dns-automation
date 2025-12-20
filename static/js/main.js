// Функции для работы с API ключами
function getApiKeys() {
    return {
        cloudflare_email: localStorage.getItem('cloudflare_email') || '',
        cloudflare_api_key: localStorage.getItem('cloudflare_api_key') || '',
        registrar_api_url: localStorage.getItem('registrar_api_url') || 'https://adm.tools/action',
        registrar_api_key: localStorage.getItem('registrar_api_key') || ''
    };
}

async function saveApiSettings() {
    const email = document.getElementById('cloudflare_email').value.trim();
    const cfKey = document.getElementById('cloudflare_api_key').value.trim();
    const regUrl = document.getElementById('registrar_api_url').value.trim();
    const regKey = document.getElementById('registrar_api_key').value.trim();
    
    if (!email || !cfKey || !regKey) {
        showSettingsStatus('⚠️ Заполните все обязательные поля!', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cloudflare_email: email,
                cloudflare_api_key: cfKey,
                registrar_api_url: regUrl,
                registrar_api_key: regKey
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            showSettingsStatus('❌ Ошибка: ' + result.error, 'error');
            return;
        }
        
        // Сохраняем также в localStorage для быстрого доступа
        localStorage.setItem('cloudflare_email', email);
        localStorage.setItem('cloudflare_api_key', cfKey);
        localStorage.setItem('registrar_api_url', regUrl);
        localStorage.setItem('registrar_api_key', regKey);
        
        showSettingsStatus('✅ Настройки сохранены на сервере!', 'success');
        
        // Очищаем поля паролей для безопасности
        setTimeout(() => {
            document.getElementById('cloudflare_api_key').value = '';
            document.getElementById('registrar_api_key').value = '';
        }, 1000);
    } catch (error) {
        showSettingsStatus('❌ Ошибка сохранения: ' + error.message, 'error');
    }
}

async function loadApiSettings() {
    try {
        // Сначала пытаемся загрузить с сервера
        const response = await fetch('/api/settings');
        const result = await response.json();
        
        if (result.cloudflare_email) {
            document.getElementById('cloudflare_email').value = result.cloudflare_email;
            document.getElementById('cloudflare_api_key').value = result.cloudflare_api_key || '';
            document.getElementById('registrar_api_url').value = result.registrar_api_url || 'https://adm.tools/action';
            document.getElementById('registrar_api_key').value = result.registrar_api_key || '';
            
            // Сохраняем в localStorage
            localStorage.setItem('cloudflare_email', result.cloudflare_email);
            localStorage.setItem('cloudflare_api_key', result.cloudflare_api_key || '');
            localStorage.setItem('registrar_api_url', result.registrar_api_url || 'https://adm.tools/action');
            localStorage.setItem('registrar_api_key', result.registrar_api_key || '');
        } else {
            // Если на сервере нет, загружаем из localStorage
            const keys = getApiKeys();
            document.getElementById('cloudflare_email').value = keys.cloudflare_email;
            document.getElementById('cloudflare_api_key').value = keys.cloudflare_api_key;
            document.getElementById('registrar_api_url').value = keys.registrar_api_url;
            document.getElementById('registrar_api_key').value = keys.registrar_api_key;
        }
    } catch (error) {
        // Если ошибка, загружаем из localStorage
        const keys = getApiKeys();
        document.getElementById('cloudflare_email').value = keys.cloudflare_email;
        document.getElementById('cloudflare_api_key').value = keys.cloudflare_api_key;
        document.getElementById('registrar_api_url').value = keys.registrar_api_url;
        document.getElementById('registrar_api_key').value = keys.registrar_api_key;
    }
}

function showSettingsStatus(message, type) {
    const statusDiv = document.getElementById('settingsStatus');
    const className = type === 'success' ? 'success-message' : 'error-message';
    statusDiv.innerHTML = `<div class="${className}">${message}</div>`;
    setTimeout(() => {
        statusDiv.innerHTML = '';
    }, 3000);
}

function checkApiKeys() {
    const keys = getApiKeys();
    if (!keys.cloudflare_email || !keys.cloudflare_api_key || !keys.registrar_api_key) {
        showError('⚠️ Сначала настройте API ключи в разделе "Настройки API"!');
        return false;
    }
    return true;
}

// Загружаем настройки при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    loadApiSettings();
});

async function runStage(stageNumber) {
    if (!checkApiKeys()) {
        return;
    }
    
    const domains = document.getElementById('domains').value.trim().split('\n').filter(d => d.trim());
    const ipAddress = document.getElementById('ip_address').value.trim();
    
    if (!domains.length) {
        showError('Пожалуйста, введите хотя бы один домен');
        return;
    }
    
    if (stageNumber === 1 && !ipAddress) {
        showError('Пожалуйста, введите IP адрес');
        return;
    }
    
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<div class="loading">Выполняется этап ' + stageNumber + '...</div>';
    
    try {
        let url = `/api/stage${stageNumber}`;
        let data = { 
            domains: domains,
            api_keys: getApiKeys()
        };
        
        if (stageNumber === 1) {
            data.ip_address = ipAddress;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.error) {
            showError(result.error);
            return;
        }
        
        displayResults(`Этап ${stageNumber}`, result.results || result);
        
    } catch (error) {
        showError('Ошибка: ' + error.message);
    }
}

async function runAllStages() {
    if (!checkApiKeys()) {
        return;
    }
    
    const domains = document.getElementById('domains').value.trim().split('\n').filter(d => d.trim());
    const ipAddress = document.getElementById('ip_address').value.trim();
    
    if (!domains.length) {
        showError('Пожалуйста, введите хотя бы один домен');
        return;
    }
    
    if (!ipAddress) {
        showError('Пожалуйста, введите IP адрес');
        return;
    }
    
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<div class="loading">Запуск всех этапов...</div>';
    
    try {
        const response = await fetch('/api/run-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                domains: domains,
                ip_address: ipAddress,
                api_keys: getApiKeys()
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            showError(result.error);
            return;
        }
        
        let html = '<h2>Результаты всех этапов</h2>';
        
        if (result.stage1) {
            html += '<div class="stage-result">';
            html += '<h3>Этап 1: Обновление A записей</h3>';
            html += displayResultsHTML(result.stage1.results || result.stage1);
            html += '</div>';
        }
        
        if (result.stage2) {
            html += '<div class="stage-result">';
            html += '<h3>Этап 2: Добавление в Cloudflare</h3>';
            html += displayResultsHTML(result.stage2.results || result.stage2);
            html += '</div>';
        }
        
        if (result.stage3) {
            html += '<div class="stage-result">';
            html += '<h3>Этап 3: Обновление NS записей</h3>';
            html += displayResultsHTML(result.stage3.results || result.stage3);
            html += '</div>';
        }
        
        if (result.stage4) {
            html += '<div class="stage-result">';
            html += '<h3>Этап 4: Настройка TLS/HTTPS</h3>';
            html += displayResultsHTML(result.stage4.results || result.stage4);
            html += '</div>';
        }
        
        resultsDiv.innerHTML = html;
        
    } catch (error) {
        showError('Ошибка: ' + error.message);
    }
}

function displayResults(title, results) {
    const resultsDiv = document.getElementById('results');
    let html = `<div class="stage-result"><h3>${title}</h3>`;
    html += displayResultsHTML(results);
    html += '</div>';
    resultsDiv.innerHTML = html;
}

function displayResultsHTML(results) {
    if (!Array.isArray(results)) {
        return '<div class="error-message">Неверный формат результатов</div>';
    }
    
    let html = '';
    results.forEach(result => {
        const statusClass = result.status === 'success' ? 'success' : 'error';
        html += `<div class="domain-result ${statusClass}">`;
        html += `<div class="domain-name">${result.domain}</div>`;
        html += `<div class="message">${result.message}</div>`;
        if (result.nameservers) {
            html += `<div class="message">NS: ${result.nameservers.join(', ')}</div>`;
        }
        html += '</div>';
    });
    
    return html;
}

function showError(message) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `<div class="error-message">${message}</div>`;
}

function showSuccess(message) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `<div class="success-message">${message}</div>`;
}

