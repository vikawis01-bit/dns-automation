# Развертывание на бесплатном хостинге

## Рекомендуемые платформы

### 1. Render.com (⭐ Рекомендуется)

**Преимущества:**
- Бесплатный tier с 750 часов/месяц
- Автоматическое развертывание из GitHub
- Бесплатный SSL сертификат
- Простая настройка

**Шаги:**

1. **Создайте аккаунт на [Render.com](https://render.com)**

2. **Подготовьте проект:**
   - Создайте файл `render.yaml` (см. ниже)
   - Убедитесь, что все файлы закоммичены в Git

3. **Создайте новый Web Service:**
   - Connect your repository (GitHub/GitLab)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment Variables: добавьте все переменные из `.env`

4. **Настройте переменные окружения в Render:**
   ```
   CLOUDFLARE_API_TOKEN=ваш_токен
   REGISTRAR_API_URL=https://api.ukraine.com.ua/v2
   REGISTRAR_API_KEY=ваш_ключ
   REGISTRAR_API_SECRET=ваш_секрет
   ```

---

### 2. Railway.app

**Преимущества:**
- $5 бесплатных кредитов/месяц
- Очень простой деплой
- Автоматический HTTPS

**Шаги:**

1. Создайте аккаунт на [Railway.app](https://railway.app)
2. New Project → Deploy from GitHub repo
3. Railway автоматически определит Python проект
4. Добавьте переменные окружения в Settings → Variables
5. Деплой произойдет автоматически

---

### 3. PythonAnywhere

**Преимущества:**
- Бесплатный tier (ограниченный)
- Простой для начинающих
- Прямой доступ к консоли

**Шаги:**

1. Создайте аккаунт на [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Загрузите файлы через Files tab
3. Создайте Web app → Manual configuration
4. Укажите путь к `app.py`
5. Настройте переменные окружения в Web → Environment variables

---

### 4. Fly.io

**Преимущества:**
- Бесплатный tier
- Глобальная сеть
- Отличная производительность

**Шаги:**

1. Установите Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Создайте `fly.toml` (см. ниже)
3. `fly launch` - создаст приложение
4. `fly secrets set CLOUDFLARE_API_TOKEN=...` - установите переменные
5. `fly deploy` - задеплойте

---

## Файлы для деплоя

### render.yaml (для Render.com)

```yaml
services:
  - type: web
    name: dns-automation
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: CLOUDFLARE_API_TOKEN
        sync: false
      - key: REGISTRAR_API_URL
        value: https://api.ukraine.com.ua/v2
      - key: REGISTRAR_API_KEY
        sync: false
      - key: REGISTRAR_API_SECRET
        sync: false
```

### fly.toml (для Fly.io)

```toml
app = "dns-automation"
primary_region = "iad"

[build]

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

### Procfile (для Heroku/Railway)

```
web: gunicorn app:app
```

---

## Быстрый старт с Render.com

1. **Создайте репозиторий на GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/ваш_username/dns-automation.git
   git push -u origin main
   ```

2. **На Render.com:**
   - New → Web Service
   - Connect GitHub repository
   - Выберите ваш репозиторий
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Add Environment Variables (все из .env)
   - Create Web Service

3. **Готово!** Ваше приложение будет доступно по адресу `https://ваш-проект.onrender.com`

---

## Важные замечания

⚠️ **Бесплатные платформы:**
- Могут "засыпать" после периода неактивности (первый запрос будет медленным)
- Имеют ограничения по ресурсам
- Могут иметь ограничения по времени работы

✅ **Рекомендации:**
- Для тестирования: Render.com или Railway.app
- Для продакшена: рассмотрите платные планы или VPS

---

## Локальное тестирование перед деплоем

```bash
# Установите зависимости
pip install -r requirements.txt

# Создайте .env файл
cp .env.example .env
# Заполните .env

# Запустите локально
python app.py

# Или с gunicorn (как на продакшене)
gunicorn app:app
```

