from flask import Flask, request, session, render_template
import threading
import webbrowser

app = Flask(__name__)
app.secret_key = "frontend-placeholder-secret-key"
APP_URL = "http://127.0.0.1:5001"


def get_placeholder_context(
    user_id=None,
    message=None,
    error=None,
    database_text=None,
    prompt_text=None,
    recommendation=None,
):
    return {
        "user_id": user_id,
        "products": None,
        "database_text": database_text,
        "prompt_text": prompt_text,
        "recommendation": recommendation,
        "message": message,
        "error": error,
    }


def build_placeholder_database_text(user_id):
    return (
        f"Заглушка базы данных для пользователя {user_id}.\n"
        "Здесь будет история покупок, которую ты позже подключишь из своей базы."
    )


def build_placeholder_prompt(user_id, database_text):
    return (
        "На основе данных пользователя составь персональную рекомендацию.\n\n"
        f"user_id: {user_id}\n"
        f"данные из базы:\n{database_text}"
    )


def build_placeholder_ai_answer():
    return (
        "Заглушка ответа нейронки. Здесь появится реальная рекомендация после "
        "подключения модели."
    )


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", **get_placeholder_context(session.get("user_id")))


@app.route("/login", methods=["POST"])
def login():
    user_id = request.form.get("user_id", "").strip()
    if not user_id.isdigit():
        return render_template(
            "index.html",
            **get_placeholder_context(error="user_id должен быть целым числом"),
        )

    session["user_id"] = int(user_id)
    return render_template(
        "index.html",
        **get_placeholder_context(
            session.get("user_id"),
            "Пользователь выбран. Подключение к базе данных будет добавлено позже.",
        ),
    )


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return render_template(
        "index.html",
        **get_placeholder_context(message="Сессия очищена."),
    )


@app.route("/history", methods=["POST"])
def history():
    user_id = session.get("user_id")
    if not user_id:
        return render_template(
            "index.html",
            **get_placeholder_context(error="Сначала авторизуйтесь по user_id"),
        )

    database_text = build_placeholder_database_text(user_id)
    prompt_text = build_placeholder_prompt(user_id, database_text)
    recommendation = build_placeholder_ai_answer()

    return render_template(
        "index.html",
        **get_placeholder_context(
            user_id,
            "Здесь появится история покупок после подключения твоей базы данных.",
            database_text=database_text,
            prompt_text=prompt_text,
            recommendation=recommendation,
        ),
    )


if __name__ == "__main__":
    threading.Timer(1.0, lambda: webbrowser.open(APP_URL)).start()
    app.run(debug=True, port=5001, use_reloader=False)
