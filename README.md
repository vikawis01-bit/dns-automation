# DNS и Cloudflare Автоматизация

Веб-приложение для автоматизации управления DNS записями и настройки Cloudflare.

## Функционал

### Этап 1: Обновление A записей у регистратора
- Ввод доменов и IP адреса
- Обновление A DNS записей через API регистратора
- Удаление всех остальных DNS записей

### Этап 2: Добавление доменов в Cloudflare
- Добавление доменов в Cloudflare через API
- Автоматический импорт A записей от регистратора
- Удаление всех записей кроме A

### Этап 3: Обновление NS записей
- Получение NS записей из Cloudflare
- Обновление NS записей у регистратора

### Этап 4: Настройка безопасности
- Установка TLS минимум версии 1.2
- Включение Always HTTPS

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

3. Заполните `.env` файл вашими API ключами:
   - Cloudflare API Token (или Email + API Key)
   - API ключи вашего регистратора

## Запуск

```bash
python app.py
```

Приложение будет доступно по адресу `http://localhost:5000`

## Развертывание на сервере

### Использование Gunicorn (рекомендуется для продакшена):

1. Установите Gunicorn:
```bash
pip install gunicorn
```

2. Запустите приложение:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Использование systemd (для автозапуска):

Создайте файл `/etc/systemd/system/dns-automation.service`:

```ini
[Unit]
Description=DNS and Cloudflare Automation
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/your/app
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl enable dns-automation
sudo systemctl start dns-automation
```

### Настройка Nginx (опционально):

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Настройка API регистратора

### Ukraine.com.ua

Приложение настроено для работы с API регистратора **ukraine.com.ua** (API v2).

**Получение API ключей:**
1. Войдите в панель управления ukraine.com.ua
2. Перейдите в раздел API
3. Создайте API ключ и секрет
4. Добавьте их в `.env` файл

**Настройка .env:**
```env
REGISTRAR_API_URL=https://api.ukraine.com.ua/v2
REGISTRAR_API_KEY=ваш_api_ключ
REGISTRAR_API_SECRET=ваш_api_секрет
```

**Документация API:** https://www.ukraine.com.ua/domains/apiv2/

Модуль `ukraine_registrar.py` содержит все необходимые функции для работы с API ukraine.com.ua:
- `ukraine_get_dns_records()` - получение DNS записей
- `ukraine_delete_dns_record()` - удаление DNS записи
- `ukraine_create_dns_record()` - создание DNS записи
- `ukraine_update_nameservers()` - обновление NS записей
- `ukraine_update_domain_a_record()` - обновление A записи (удаляет все остальные)

### Другие регистраторы

Если вы используете другого регистратора, см. файл `registrar_examples.py` с примерами для:
- Namecheap
- GoDaddy
- Name.com

Адаптируйте функции в `ukraine_registrar.py` под API вашего регистратора.

## Безопасность

- Никогда не коммитьте файл `.env` в репозиторий
- Используйте HTTPS для продакшена
- Ограничьте доступ к приложению через файрвол
- Регулярно обновляйте зависимости

## Лицензия

MIT

