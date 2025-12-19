# Настройка для Ukraine.com.ua

## Получение API ключей

1. Войдите в панель управления на https://www.ukraine.com.ua/
2. Перейдите в раздел **API** (обычно находится в настройках аккаунта)
3. Создайте новый API ключ и секрет
4. Сохраните их в безопасном месте

## Настройка .env файла

Создайте файл `.env` в корне проекта:

```env
# Cloudflare API
CLOUDFLARE_API_TOKEN=your_cloudflare_token
# ИЛИ используйте Email + API Key:
# CLOUDFLARE_EMAIL=your_email@example.com
# CLOUDFLARE_API_KEY=your_cloudflare_api_key

# Ukraine.com.ua API
REGISTRAR_API_URL=https://api.ukraine.com.ua/v2
REGISTRAR_API_KEY=ваш_api_ключ_от_ukraine
REGISTRAR_API_SECRET=ваш_api_секрет_от_ukraine
```

## Проверка API

Если структура API ukraine.com.ua отличается от ожидаемой, вам может потребоваться адаптировать функции в `ukraine_registrar.py`.

### Типичные проблемы:

1. **Формат ответа API** - проверьте структуру JSON ответа
2. **Названия полей** - могут быть `id`, `record_id`, `_id` и т.д.
3. **Схема аутентификации** - Basic Auth или Bearer Token
4. **Формат данных** - структура для создания/обновления записей

### Тестирование API:

Вы можете протестировать API вручную:

```python
import requests
import base64

# Basic Auth
credentials = f"{REGISTRAR_API_KEY}:{REGISTRAR_API_SECRET}"
encoded = base64.b64encode(credentials.encode()).decode()
headers = {
    'Authorization': f'Basic {encoded}',
    'Content-Type': 'application/json'
}

# Тест получения DNS записей
response = requests.get(
    f"{REGISTRAR_API_URL}/domains/example.com/dns",
    headers=headers
)
print(response.json())
```

## Документация

- **API v2:** https://www.ukraine.com.ua/domains/apiv2/
- **Поддержка:** обратитесь в техподдержку ukraine.com.ua для уточнения структуры API

## Поддержка

Если у вас возникли проблемы с интеграцией, проверьте:
1. Правильность API ключей
2. Формат URL (может быть `/api/v2/` вместо `/v2/`)
3. Структуру ответов API (может отличаться от ожидаемой)

