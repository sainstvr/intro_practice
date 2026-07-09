import os
import sqlite3

import requests
from dotenv import load_dotenv


load_dotenv()


def get_user_history(user_id):
    loginom_url = os.getenv("LOGINOM_URL")

    if not loginom_url:
        return [
            {
                "product_name": "Banana",
                "aisle": "fresh fruits",
                "department": "produce",
                "department_rus": "фрукты и овощи",
                "order_count": 5,
            },
            {
                "product_name": "Milk",
                "aisle": "milk",
                "department": "dairy eggs",
                "department_rus": "молочные продукты",
                "order_count": 3,
            },
            {
                "product_name": "Yogurt",
                "aisle": "yogurt",
                "department": "dairy eggs",
                "department_rus": "молочные продукты",
                "order_count": 2,
            },
        ]

    response = requests.get(loginom_url, params={"user_id": user_id}, timeout=15)

    if response.status_code >= 400:
        try:
            error_data = response.json()
            detail = error_data.get("detail", "")
            inner = error_data.get("inner", {}).get("message", "")
            message = f"{detail}. {inner}".strip(". ")
        except ValueError:
            message = response.text

        raise RuntimeError(f"Loginom вернул ошибку {response.status_code}: {message}")

    data = response.json()

    if isinstance(data, list):
        return data

    if "products" in data:
        return data["products"]

    if "rows" in data:
        return data["rows"]

    if "data" in data:
        return data["data"]

    if "DataSet" in data:
        return data["DataSet"]["Rows"]

    return data


def build_products_text(products):
    lines = []

    for product in products:
        line = (
            f"{product['product_name']} - "
            f"категория: {product['department_rus']}, "
            f"количество покупок: {product['order_count']}"
        )
        lines.append(line)

    return "\n".join(lines)


def build_category_stats(products):
    stats = {}

    for product in products:
        category = product.get("department_rus") or product.get("department") or "Без категории"
        order_count = product.get("order_count", 0)
        stats[category] = stats.get(category, 0) + order_count

    result = []
    for category, order_count in stats.items():
        result.append({
            "category": category,
            "order_count": order_count,
        })

    result.sort(key=lambda item: item["order_count"], reverse=True)
    return result


def get_popular_recommendations(user_id, limit=10):
    db_path = os.getenv("INSTACART_DB_PATH", "loginom/instacart_db.sqlite")

    if not os.path.exists(db_path):
        return []

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    query = """
        WITH user_categories AS (
            SELECT DISTINCT p.department
            FROM Orders o
            JOIN orders_prior op ON op.order_id = o.order_id
            JOIN products p ON p.product_id = op.product_id
            WHERE o.user_id = ?
                AND o.eval_set = 'prior'
        ),
        user_products AS (
            SELECT DISTINCT op.product_id
            FROM Orders o
            JOIN orders_prior op ON op.order_id = o.order_id
            WHERE o.user_id = ?
                AND o.eval_set = 'prior'
        )
        SELECT
            p.product_name,
            p.aisle,
            p.department,
            p.department_rus,
            COUNT(*) AS popularity
        FROM orders_prior op
        JOIN products p ON p.product_id = op.product_id
        WHERE p.department IN (SELECT department FROM user_categories)
            AND p.product_id NOT IN (SELECT product_id FROM user_products)
        GROUP BY
            p.product_id,
            p.product_name,
            p.aisle,
            p.department,
            p.department_rus
        ORDER BY popularity DESC, p.product_name
        LIMIT ?
    """

    rows = connection.execute(query, (user_id, user_id, limit)).fetchall()
    connection.close()

    max_popularity = 0
    if rows:
        max_popularity = rows[0]["popularity"]

    recommendations = []
    for row in rows:
        item = dict(row)
        item["total_orders"] = item["popularity"]
        item["popularity_score"] = round(item["popularity"] / max_popularity * 10, 1)
        recommendations.append(item)

    return recommendations


def build_codex_prompt(products_text):
    system_prompt = """Ты — персональный помощник покупателя в продуктовом онлайн-магазине.
Твоя задача — анализировать историю покупок клиента и давать ему понятные,
дружелюбные рекомендации прямо в его личном кабинете.
Обращайся к клиенту на "вы", тепло и по-человечески.
Пиши кратко — не более 5–6 предложений."""

    user_prompt = f"""Вот список товаров, которые клиент покупает чаще всего:
{products_text}

Напишите клиенту короткий персональный анализ его покупок.
Начните с того, что вы заметили в его предпочтениях.
Дайте 1–2 дружеских совета — например, что стоит попробовать добавить
или на что обратить внимание. Пишите так, как будто клиент читает это
в своём личном кабинете."""

    return system_prompt + "\n\n" + user_prompt


def ask_codex(user_id, products_text):
    # Пока Codex заменен простой заглушкой.
    # Когда будет готов реальный способ подключения, менять нужно только эту функцию.
    return (
        "Я заметил, что вы часто выбираете фрукты и молочные продукты. "
        "Похоже, вам нравятся простые и полезные продукты для ежедневного рациона. "
        "Попробуйте добавить яблоки или творог: они хорошо сочетаются с тем, что вы уже покупаете. "
        "Также можно обратить внимание на натуральный йогурт без добавок."
    )
