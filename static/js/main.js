async function runStage(stageNumber) {
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
        let data = { domains: domains };
        
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
                ip_address: ipAddress
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

