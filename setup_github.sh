#!/bin/bash

# Установка GitHub CLI и автоматизация деплоя

echo "🔧 Настройка GitHub CLI для автоматического деплоя..."

# Проверка Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew не установлен"
    echo ""
    echo "Установите Homebrew:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    echo "Или установите GitHub CLI вручную:"
    echo "  https://cli.github.com/"
    exit 1
fi

echo "✅ Homebrew установлен"

# Установка GitHub CLI
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI уже установлен"
    gh --version | head -1
else
    echo "📦 Устанавливаю GitHub CLI..."
    brew install gh
    
    if [ $? -eq 0 ]; then
        echo "✅ GitHub CLI установлен"
    else
        echo "❌ Ошибка при установке GitHub CLI"
        exit 1
    fi
fi

# Проверка авторизации
echo ""
echo "🔐 Проверка авторизации GitHub..."

if gh auth status &> /dev/null; then
    echo "✅ Вы уже авторизованы в GitHub"
    GITHUB_USER=$(gh api user --jq .login 2>/dev/null)
    echo "👤 Пользователь: $GITHUB_USER"
else
    echo "⚠️  Требуется авторизация в GitHub"
    echo ""
    echo "Запускаю процесс авторизации..."
    echo "Следуйте инструкциям на экране"
    echo ""
    gh auth login
    
    if [ $? -eq 0 ]; then
        GITHUB_USER=$(gh api user --jq .login 2>/dev/null)
        echo "✅ Авторизация успешна! Пользователь: $GITHUB_USER"
    else
        echo "❌ Ошибка при авторизации"
        exit 1
    fi
fi

echo ""
echo "🚀 Теперь запустите auto_deploy.sh для автоматического создания репозитория:"
echo "   ./auto_deploy.sh"

