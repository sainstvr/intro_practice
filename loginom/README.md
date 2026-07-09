# Loginom

В этой папке лежит проект Loginom:

- `instacart_ws_хамчиев_волков_умаров.lgp` — основной проект.
- `instacart_ws_хамчиев_волков_умаров.~lgp` — временная/резервная копия проекта.
- `instacart_ws_хамчиев_волков_умаров.lgp.lck` — lock-файл.

Что найдено внутри проекта:

- опубликованный узел: `GetUserHistory`;
- входная переменная: `user_id`;
- подключение к базе: `../instacart_db.sqlite`;
- выходные поля: `product_name`, `aisle`, `department`, `department_rus`, `order_count`.

Как это связано с Flask:

1. Открыть `.lgp` в Loginom.
2. Проверить, что рядом с проектом доступна база `instacart_db.sqlite`.
3. Опубликовать узел `GetUserHistory` как сервис.
4. Скопировать URL сервиса в файл `.env`:

```env
LOGINOM_URL=адрес_опубликованного_сервиса
```

Flask отправляет в Loginom GET-запрос с параметром:

```text
?user_id=1
```

Ожидаемый ответ:

```json
[
  {
    "product_name": "Banana",
    "aisle": "fresh fruits",
    "department": "produce",
    "department_rus": "фрукты и овощи",
    "order_count": 5
  }
]
```
