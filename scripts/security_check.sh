#!/bin/bash

# 🔒 Проверка безопасности - поиск хардкодных паролей

echo "🔒 Проверка безопасности проекта"
echo "================================"

# Загружаем переменные окружения
if [ -f ".env" ]; then
    source .env
    echo "✅ Файл .env найден"
else
    echo "❌ Файл .env не найден!"
    exit 1
fi

# Проверяем наличие хардкодных паролей
echo ""
echo "🔍 Поиск хардкодных паролей..."

# Ищем подозрительные паттерны
SUSPICIOUS_PATTERNS=(
    "password.*=.*['\"][^'\"]*['\"]"
    "Password.*=.*['\"][^'\"]*['\"]"
    "PASSWORD.*=.*['\"][^'\"]*['\"]"
    "pass.*=.*['\"][^'\"]*['\"]"
    "Pass.*=.*['\"][^'\"]*['\"]"
    "PASS.*=.*['\"][^'\"]*['\"]"
)

FOUND_ISSUES=0

for pattern in "${SUSPICIOUS_PATTERNS[@]}"; do
    # Ищем в файлах проекта (исключая venv, .git, документацию и скрипты проверки)
    RESULTS=$(grep -r -E "$pattern" . --include="*.py" --include="*.yml" --include="*.sh" --include="*.sql" --exclude-dir=venv --exclude-dir=.git --exclude="security_check.sh" --exclude="ENV_SETUP.md" 2>/dev/null | grep -v "os.getenv\|getenv\|System.getenv\|process.env\|MISSING_VARS" || true)
    
    if [ -n "$RESULTS" ]; then
        echo "⚠️  Найдены подозрительные пароли:"
        echo "$RESULTS"
        FOUND_ISSUES=$((FOUND_ISSUES + 1))
    fi
done

# Проверяем использование переменных окружения
echo ""
echo "✅ Проверка использования переменных окружения..."

ENV_VARS=("DB_PASSWORD" "PGADMIN_PASSWORD" "API_ID_TG" "API_HASH_TG" "BOT_TOKEN")

for var in "${ENV_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Переменная $var не задана в .env"
        FOUND_ISSUES=$((FOUND_ISSUES + 1))
    else
        echo "✅ $var: ${!var:0:10}..."
    fi
done

# Проверяем права доступа к .env
echo ""
echo "🔐 Проверка прав доступа к .env файлу..."
ENV_PERMS=$(stat -c "%a" .env 2>/dev/null || echo "не найден")

if [ "$ENV_PERMS" = "600" ] || [ "$ENV_PERMS" = "640" ]; then
    echo "✅ Права доступа к .env: $ENV_PERMS (безопасно)"
else
    echo "⚠️  Права доступа к .env: $ENV_PERMS (рекомендуется 600)"
    echo "   Исправьте: chmod 600 .env"
fi

# Проверяем .gitignore
echo ""
echo "📁 Проверка .gitignore..."
if grep -q "\.env" .gitignore 2>/dev/null; then
    echo "✅ .env файл исключен из Git"
else
    echo "❌ .env файл НЕ исключен из Git!"
    echo "   Добавьте в .gitignore: echo '.env' >> .gitignore"
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
fi

# Итоговый результат
echo ""
echo "================================"
if [ $FOUND_ISSUES -eq 0 ]; then
    echo "🎉 Проверка безопасности пройдена успешно!"
    echo "✅ Все пароли используют переменные окружения"
    echo "✅ Нет хардкодных паролей в коде"
else
    echo "⚠️  Найдено $FOUND_ISSUES проблем безопасности"
    echo "🔧 Исправьте найденные проблемы перед развертыванием"
fi

echo ""
echo "💡 Рекомендации по безопасности:"
echo "   - Регулярно меняйте пароли"
echo "   - Используйте сложные пароли (12+ символов)"
echo "   - Не коммитьте .env файл в Git"
echo "   - Ограничьте права доступа к .env файлу"
echo "   - Используйте разные пароли для разных сред"
