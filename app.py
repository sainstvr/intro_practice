from flask import Flask, render_template, request

from business_rules import ask_codex, build_codex_prompt, build_products_text, get_user_history


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history", methods=["POST"])
def history():
    user_id_text = request.form.get("user_id", "")

    if not user_id_text.isdigit():
        return render_template(
            "index.html",
            error="user_id должен быть целым числом",
        )

    user_id = int(user_id_text)

    try:
        products = get_user_history(user_id)
        products_text = build_products_text(products)
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
        codex_prompt=codex_prompt,
        recommendation=recommendation,
    )


if __name__ == "__main__":
    app.run(debug=True)
