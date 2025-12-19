// Загрузка текущих настроек при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    loadSettings();
});

// Загрузка настроек с сервера
async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        if (response.ok) {
            const settings = await response.json();
            
            // Заполняем форму текущими значениями
            if (settings.cloudflare_email) {
                document.getElementById('cloudflare_email').value = settings.cloudflare_email;
            }
            if (settings.cloudflare_api_key) {
                document.getElementById('cloudflare_api_key').value = settings.cloudflare_api_key;
            }
            if (settings.registrar_api_url) {
                document.getElementById('registrar_api_url').value = settings.registrar_api_url;
            }
            if (settings.registrar_api_key) {
                document.getElementById('registrar_api_key').value = settings.registrar_api_key;
            }
        }
    } catch (error) {
        console.error('Ошибка загрузки настроек:', error);
    }
}

// Обработка отправки формы
document.getElementById('settingsForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        cloudflare_email: document.getElementById('cloudflare_email').value.trim(),
        cloudflare_api_key: document.getElementById('cloudflare_api_key').value.trim(),
        registrar_api_url: document.getElementById('registrar_api_url').value.trim(),
        registrar_api_key: document.getElementById('registrar_api_key').value.trim()
    };
    
    // Валидация
    if (!formData.cloudflare_email || !formData.cloudflare_api_key) {
        showAlert('Пожалуйста, заполните все поля Cloudflare', 'error');
        return;
    }
    
    if (!formData.registrar_api_url || !formData.registrar_api_key) {
        showAlert('Пожалуйста, заполните все поля Ukraine.com.ua', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('✅ Настройки успешно сохранены!', 'success');
            // Обновляем настройки в памяти приложения
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showAlert('❌ Ошибка: ' + (result.error || 'Не удалось сохранить настройки'), 'error');
        }
    } catch (error) {
        showAlert('❌ Ошибка: ' + error.message, 'error');
    }
});

// Показать уведомление
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
    
    alertContainer.innerHTML = `<div class="alert ${alertClass}">${message}</div>`;
    
    // Автоматически скрыть через 5 секунд
    setTimeout(() => {
        alertContainer.innerHTML = '';
    }, 5000);
}

