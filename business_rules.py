import os

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


def get_order_times(products):
    times = []

    for product in products:
        value = (
            product.get("order_time")
            or product.get("order_hour_of_day")
            or product.get("last_order_time")
        )

        if value is not None and value not in times:
            times.append(value)

    return times


def find_stopped_products(products):
    stopped_products = []

    for product in products:
        old_count = product.get("old_order_count") or product.get("previous_order_count")
        recent_count = product.get("recent_order_count") or product.get("last_order_count")

        if old_count and recent_count == 0:
            stopped_products.append(product)

    return stopped_products


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
