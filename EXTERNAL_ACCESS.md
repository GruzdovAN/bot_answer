# Внешний доступ к PostgreSQL

## 🔐 Учетные данные

### PostgreSQL
- **Хост**: `YOUR_SERVER_IP` (замените на IP вашего сервера)
- **Порт**: `5432`
- **База данных**: `${DB_NAME:-telegram_bot}` (из .env файла)
- **Пользователь**: `${DB_USER:-telegram_admin}` (из .env файла)
- **Пароль**: `${DB_PASSWORD}` (из .env файла)

### pgAdmin
- **URL**: `http://YOUR_SERVER_IP:8080`
- **Email**: `${PGADMIN_EMAIL:-admin@telegram-bot.com}` (из .env файла)
- **Пароль**: `${PGADMIN_PASSWORD}` (из .env файла)

### Настройка переменных окружения
Все пароли и логины настраиваются в файле `.env`. Скопируйте `env.example` в `.env` и заполните своими данными:

```bash
cp env.example .env
nano .env
```

## 🔌 Примеры подключения

### Python (psycopg2)
```python
import psycopg2
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Подключение к базе данных
conn = psycopg2.connect(
    host="YOUR_SERVER_IP",
    port=5432,
    database=os.getenv("DB_NAME", "telegram_bot"),
    user=os.getenv("DB_USER", "telegram_admin"),
    password=os.getenv("DB_PASSWORD")
)

# Выполнение запроса
cursor = conn.cursor()
cursor.execute("SELECT * FROM messages LIMIT 10;")
results = cursor.fetchall()
print(results)

conn.close()
```

### Python (SQLAlchemy)
```python
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Строка подключения
DATABASE_URL = f"postgresql://{os.getenv('DB_USER', 'telegram_admin')}:{os.getenv('DB_PASSWORD')}@YOUR_SERVER_IP:5432/{os.getenv('DB_NAME', 'telegram_bot')}"

# Создание движка
engine = create_engine(DATABASE_URL, echo=True)

# Подключение
with engine.connect() as conn:
    result = conn.execute("SELECT * FROM messages LIMIT 10;")
    for row in result:
        print(row)
```

### Node.js (pg)
```javascript
const { Client } = require('pg');

const client = new Client({
    host: 'YOUR_SERVER_IP',
    port: 5432,
    database: 'telegram_bot',
    user: 'telegram_admin',
    password: process.env.DB_PASSWORD
});

client.connect()
    .then(() => {
        return client.query('SELECT * FROM messages LIMIT 10;');
    })
    .then(result => {
        console.log(result.rows);
    })
    .catch(err => {
        console.error(err);
    })
    .finally(() => {
        client.end();
    });
```

### PHP (PDO)
```php
<?php
$host = 'YOUR_SERVER_IP';
$port = 5432;
$dbname = 'telegram_bot';
$user = 'telegram_admin';
$password = getenv('DB_PASSWORD');

try {
    $pdo = new PDO(
        "pgsql:host=$host;port=$port;dbname=$dbname",
        $user,
        $password
    );
    
    $stmt = $pdo->query('SELECT * FROM messages LIMIT 10;');
    $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    foreach ($results as $row) {
        print_r($row);
    }
} catch (PDOException $e) {
    echo "Ошибка подключения: " . $e->getMessage();
}
?>
```

### Java (JDBC)
```java
import java.sql.*;

public class PostgreSQLConnection {
    public static void main(String[] args) {
        String url = "jdbc:postgresql://YOUR_SERVER_IP:5432/telegram_bot";
        String user = "telegram_admin";
        String password = System.getenv("DB_PASSWORD");
        
        try (Connection conn = DriverManager.getConnection(url, user, password)) {
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT * FROM messages LIMIT 10;");
            
            while (rs.next()) {
                System.out.println(rs.getString("text"));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
```

## 📊 Основные таблицы

### messages
```sql
SELECT 
    m.id,
    m.telegram_id,
    m.text,
    m.created_at,
    u.username,
    u.first_name,
    c.title as chat_title
FROM messages m
LEFT JOIN users u ON m.user_id = u.id
LEFT JOIN chats c ON m.chat_id = c.id
ORDER BY m.created_at DESC
LIMIT 10;
```

### bot_responses
```sql
SELECT 
    br.response_text,
    br.response_type,
    br.trigger_keyword,
    br.response_time_ms,
    br.is_successful,
    br.created_at,
    m.text as original_message
FROM bot_responses br
JOIN messages m ON br.original_message_id = m.id
ORDER BY br.created_at DESC
LIMIT 10;
```

### Статистика
```sql
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_messages,
    COUNT(CASE WHEN is_bot_response = true THEN 1 END) as bot_responses
FROM messages
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

## 🔒 Безопасность

1. **Сложный пароль**: Используется пароль с 32 символами, включая спецсимволы
2. **Аутентификация**: Обязательная аутентификация для всех подключений
3. **Ограничения**: Настроены таймауты и лимиты подключений
4. **Логирование**: Включено логирование всех подключений и медленных запросов
5. **Переменные окружения**: Все пароли хранятся в .env файле

## ⚠️ Важные замечания

1. Замените `YOUR_SERVER_IP` на реальный IP адрес вашего сервера
2. Убедитесь, что порт 5432 открыт в файрволе
3. Для продакшена рекомендуется настроить SSL сертификаты
4. Регулярно меняйте пароли
5. Мониторьте логи подключений
