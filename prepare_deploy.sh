#!/bin/bash

# Скрипт для автоматической подготовки к деплою

echo "🚀 Подготовка проекта к деплою..."

# Проверка наличия необходимых файлов
echo "📋 Проверка файлов..."
required_files=("app.py" "requirements.txt" "Procfile" "render.yaml" "config.py")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ Отсутствуют файлы: ${missing_files[*]}"
    exit 1
fi

echo "✅ Все необходимые файлы на месте"

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден"
    if [ -f ".env.example" ]; then
        echo "📝 Создаю .env из примера..."
        cp .env.example .env
        echo "⚠️  ВАЖНО: Заполните .env файл вашими API ключами!"
    fi
else
    echo "✅ Файл .env существует"
fi

# Проверка .gitignore
if [ ! -f ".gitignore" ]; then
    echo "📝 Создаю .gitignore..."
    cat > .gitignore << EOF
__pycache__/
*.py[cod]
*\$py.class
*.so
.Python
env/
venv/
ENV/
.venv
.env
*.log
.DS_Store
instance/
.webassets-cache
EOF
    echo "✅ .gitignore создан"
else
    echo "✅ .gitignore существует"
fi

# Инициализация git (если еще не инициализирован)
if [ ! -d ".git" ]; then
    echo "📦 Инициализация Git репозитория..."
    git init
    git branch -M main
    echo "✅ Git инициализирован"
else
    echo "✅ Git репозиторий уже существует"
fi

# Проверка зависимостей
echo "📦 Проверка зависимостей..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask не установлен. Установите зависимости: pip install -r requirements.txt"
else
    echo "✅ Основные зависимости установлены"
fi

echo ""
echo "✅ Подготовка завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Заполните .env файл вашими API ключами"
echo "2. Создайте репозиторий на GitHub:"
echo "   git add ."
echo "   git commit -m 'Initial commit'"
echo "   git remote add origin https://github.com/ВАШ_USERNAME/dns-automation.git"
echo "   git push -u origin main"
echo "3. Следуйте инструкциям в DEPLOY_QUICK.md"
echo ""

