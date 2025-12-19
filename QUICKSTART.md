# Быстрый старт

## 1. Установка

```bash
# Автоматическая установка
./deploy.sh

# Или вручную:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Настройка

Скопируйте `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
nano .env  # или используйте любой редактор
```

### Cloudflare API

Получите API Token на https://dash.cloudflare.com/profile/api-tokens

Или используйте Email + Global API Key (менее безопасно)

### API Регистратора (Ukraine.com.ua)

Приложение настроено для работы с **ukraine.com.ua** (API v2).

1. Войдите в панель управления ukraine.com.ua
2. Перейдите в раздел API и создайте ключи
3. Добавьте в `.env`:
```env
REGISTRAR_API_URL=https://api.ukraine.com.ua/v2
REGISTRAR_API_KEY=ваш_ключ
REGISTRAR_API_SECRET=ваш_секрет
```

**Документация:** https://www.ukraine.com.ua/domains/apiv2/

## 3. Запуск

### Разработка:
```bash
source venv/bin/activate
python app.py
```

### Продакшен:
```bash
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 4. Использование

1. Откройте браузер: `http://localhost:5000` (или ваш домен)
2. Введите домены (по одному на строку)
3. Введите IP адрес
4. Нажмите нужный этап или "Запустить все этапы"

## Важно!

⚠️ **Приложение уже настроено для работы с ukraine.com.ua!**

Если структура API ukraine.com.ua отличается от ожидаемой, адаптируйте функции в `ukraine_registrar.py`:
- `ukraine_get_dns_records()` - получение DNS записей
- `ukraine_delete_dns_record()` - удаление записей
- `ukraine_create_dns_record()` - создание записей
- `ukraine_update_nameservers()` - обновление NS

Для других регистраторов см. `registrar_examples.py` с примерами для Namecheap, GoDaddy и др.

