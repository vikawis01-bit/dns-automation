# 🔑 API Ключи - Упрощенная версия

## ✅ Что нужно добавить на Render.com:

### 1. Cloudflare (Global API Key):

```
Key: CLOUDFLARE_EMAIL
Value: ваш_email@example.com
```

```
Key: CLOUDFLARE_API_KEY
Value: ваш_global_api_key_от_cloudflare
```

**Где взять Global API Key:**
1. https://dash.cloudflare.com/profile/api-tokens
2. Прокрутите вниз до раздела **"API Keys"**
3. Нажмите **"View"** рядом с **"Global API Key"**
4. Введите пароль от Cloudflare
5. Скопируйте ключ

---

### 2. Ukraine.com.ua (только API ключ):

```
Key: REGISTRAR_API_URL
Value: https://api.ukraine.com.ua/v2
```

```
Key: REGISTRAR_API_KEY
Value: ваш_api_ключ_от_ukraine
```

**Где взять:**
1. Панель управления ukraine.com.ua
2. Раздел **"API"** или **"Настройки"** → **"API"**
3. Скопируйте API ключ

---

## 📋 Итого 4 переменные:

1. `CLOUDFLARE_EMAIL` = ваш email
2. `CLOUDFLARE_API_KEY` = Global API Key от Cloudflare
3. `REGISTRAR_API_URL` = `https://api.ukraine.com.ua/v2`
4. `REGISTRAR_API_KEY` = API ключ от ukraine.com.ua

---

## 🎯 Где вводить на Render.com:

1. Откройте ваш проект
2. Вкладка **"Environment"**
3. **"Add Environment Variable"**
4. Добавьте все 4 переменные
5. Сохраните

---

**Готово!** После добавления приложение заработает! 🚀

