#!/bin/bash

# Автоматический деплой через GitHub CLI

echo "🚀 Автоматический деплой проекта..."

# Проверка GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI не установлен"
    echo ""
    echo "Установите GitHub CLI:"
    echo "  macOS: brew install gh"
    echo "  или: https://cli.github.com/"
    echo ""
    echo "После установки выполните: gh auth login"
    exit 1
fi

# Проверка авторизации
if ! gh auth status &> /dev/null; then
    echo "⚠️  Вы не авторизованы в GitHub CLI"
    echo "Выполните: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI установлен и авторизован"

# Получаем имя пользователя
GITHUB_USER=$(gh api user --jq .login 2>/dev/null)
if [ -z "$GITHUB_USER" ]; then
    echo "❌ Не удалось получить имя пользователя GitHub"
    exit 1
fi

echo "👤 GitHub пользователь: $GITHUB_USER"

# Название репозитория
REPO_NAME="dns-automation"
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME"

# Проверка существования репозитория
if gh repo view "$GITHUB_USER/$REPO_NAME" &> /dev/null; then
    echo "⚠️  Репозиторий $REPO_NAME уже существует"
    read -p "Перезаписать? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Отменено"
        exit 1
    fi
    echo "🔄 Обновляю существующий репозиторий..."
else
    echo "📦 Создаю новый репозиторий на GitHub..."
    gh repo create "$REPO_NAME" --public --source=. --remote=origin --push 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Репозиторий создан и код запушен!"
    else
        echo "⚠️  Репозиторий уже существует или ошибка при создании"
        echo "🔄 Пробую подключить существующий репозиторий..."
        
        # Проверяем, есть ли уже remote
        if git remote get-url origin &> /dev/null; then
            echo "✅ Remote origin уже настроен"
        else
            git remote add origin "$REPO_URL.git"
            echo "✅ Remote origin добавлен"
        fi
        
        # Пушим код
        echo "📤 Отправляю код на GitHub..."
        git push -u origin main
    fi
fi

echo ""
echo "✅ Готово! Репозиторий: $REPO_URL"
echo ""
echo "📝 Следующие шаги для деплоя на Render.com:"
echo "1. Зайдите на https://render.com"
echo "2. New → Web Service"
echo "3. Connect GitHub → выберите $REPO_NAME"
echo "4. Build: pip install -r requirements.txt"
echo "5. Start: gunicorn app:app"
echo "6. Добавьте переменные окружения (API ключи)"
echo "7. Deploy!"
echo ""
echo "Или используйте Railway.app:"
echo "1. https://railway.app → New Project"
echo "2. Deploy from GitHub → выберите $REPO_NAME"
echo "3. Добавьте переменные окружения"
echo "4. Готово!"

