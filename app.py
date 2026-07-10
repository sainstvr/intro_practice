from flask import Flask, render_template, request, session

from business_rules import (
    ask_codex,
    build_category_stats,
    build_codex_prompt,
    build_products_text,
    get_popular_recommendations,
    get_user_history,
)


app = Flask(__name__)
app.secret_key = "intro-practice-secret-key"


@app.route("/")
def index():
    return render_template("index.html", user_id=session.get("user_id"))


@app.route("/login", methods=["POST"])
def login():
    user_id_text = request.form.get("user_id", "")

    if not user_id_text.isdigit():
        return render_template(
            "index.html",
            error="user_id должен быть целым числом",
        )

    user_id = int(user_id_text)

    if user_id <= 0:
        return render_template(
            "index.html",
            error="user_id должен быть больше нуля",
        )

    try:
        products = get_user_history(user_id)
    except Exception as error:
        return render_template(
            "index.html",
            user_id=user_id,
            error=f"Ошибка при проверке клиента: {error}",
        )

    if not products:
        return render_template(
            "index.html",
            error=f"Клиент с user_id {user_id} не найден.",
        )

    session["user_id"] = user_id

    return render_template(
        "index.html",
        user_id=user_id,
        message="Пользователь выбран. Теперь можно запустить анализ покупок.",
    )


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return render_template("index.html", message="Пользователь сброшен.")


@app.route("/history", methods=["POST"])
def history():
    user_id = session.get("user_id")

    if not user_id:
        return render_template(
            "index.html",
            error="Сначала введите user_id.",
        )

    try:
        products = get_user_history(user_id)
        if not products:
            return render_template(
                "index.html",
                user_id=user_id,
                error=f"Клиент с user_id {user_id} не найден.",
            )

        products_text = build_products_text(products)
        category_stats = build_category_stats(products)
        popular_recommendations = get_popular_recommendations(user_id)
        codex_prompt = build_codex_prompt(products_text)
        recommendation = ask_codex(user_id, products_text)
    except Exception as error:
        return render_template(
            "index.html",
            user_id=user_id,
            error=f"Ошибка: {error}",
        )

    return render_template(
        "index.html",
        user_id=user_id,
        products=products,
        category_stats=category_stats,
        popular_recommendations=popular_recommendations,
        message="Анализ выполнен.",
        codex_prompt=codex_prompt,
        recommendation=recommendation,
    )


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

