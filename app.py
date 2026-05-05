from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "translogix-secret-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

# ------------------- Telegram -------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_ADMINS = [
    admin.strip()
    for admin in os.getenv("TELEGRAM_ADMINS", "1016799185").split(",")
    if admin.strip()
]

# ------------------- WhatsApp (Green-API) -------------------
GREEN_ID_INSTANCE = os.getenv("GREEN_ID_INSTANCE", "")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN", "")

WHATSAPP_ROUTES = {
    "astana-almaty": ["77055394342"],
    "almaty-astana": ["77761546797"],
    "kazakhstan-logistics": ["77055394342", "77761546797"],
}


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ------------------- Telegram -------------------
def send_telegram(name, phone, message, direction):
    if not TELEGRAM_TOKEN or not TELEGRAM_ADMINS:
        print("Telegram credentials are not configured.")
        return

    route_names = {
        "astana-almaty": "Астана - Караганда - Алматы",
        "almaty-astana": "Алматы - Караганда - Астана",
        "kazakhstan-logistics": "Логистика / Доставка по Казахстану",
    }

    text = (
        f"📦 Новая заявка с сайта TransLogix\n\n"
        f"🛣 Направление: {route_names.get(direction, direction)}\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"📝 Описание груза: {message}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    for chat_id in TELEGRAM_ADMINS:
        try:
            resp = requests.post(
                url,
                data={"chat_id": chat_id, "text": text},
                timeout=10
            )
            print("Telegram status:", resp.status_code, resp.text)
        except Exception as e:
            print("Telegram send error:", e)


# ------------------- WhatsApp -------------------
def send_whatsapp(name, phone, message, direction):
    if not GREEN_ID_INSTANCE or not GREEN_API_TOKEN:
        print("WhatsApp Green API credentials are not configured.")
        return

    route_names = {
        "astana-almaty": "Астана - Караганда - Алматы",
        "almaty-astana": "Алматы - Караганда - Астана",
        "kazakhstan-logistics": "Логистика / Доставка по Казахстану",
    }

    admins = WHATSAPP_ROUTES.get(direction, [])
    if not admins:
        print("No WhatsApp admins configured for route:", direction)
        return

    text = (
        "Новая заявка с сайта TransLogix\n\n"
        f"Маршрут: {route_names.get(direction, direction)}\n"
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Груз: {message}"
    )

    url = f"https://api.green-api.com/waInstance{GREEN_ID_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"

    for admin in admins:
        payload = {
            "chatId": f"{admin}@c.us",
            "message": text
        }

        try:
            resp = requests.post(url, json=payload, timeout=15)
            print("WA STATUS:", resp.status_code, resp.text)
        except Exception as e:
            print("WhatsApp send error:", e)


# ------------------- База -------------------
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            direction TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ------------------- Главная -------------------
@app.route("/")
def home():
    success = request.args.get("success")
    return render_template("index.html", success=success)


# ------------------- Отправка формы -------------------
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    message = request.form.get("message", "").strip()
    direction = request.form.get("direction", "").strip()

    if not all([name, phone, message, direction]):
        flash("Пожалуйста, заполните обязательные поля.")
        return redirect(url_for("home"))

    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO applications (name, phone, message, direction)
                VALUES (?, ?, ?, ?)
            """, (name, phone, message, direction))
            conn.commit()
    except Exception as e:
        print(f"Ошибка базы: {e}")
        flash("Ошибка сохранения заявки.")
        return redirect(url_for("home"))

    try:
        send_telegram(name, phone, message, direction)
    except Exception as e:
        print(f"Ошибка Telegram: {e}")

    try:
        send_whatsapp(name, phone, message, direction)
    except Exception as e:
        print(f"Ошибка WhatsApp: {e}")

    return redirect(url_for("home", success=1))


# ------------------- Админка -------------------
@app.route("/admin")
def admin():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM applications ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return render_template("admin.html", data=data)


# ------------------- Удаление -------------------
@app.route("/delete/<int:application_id>")
def delete(application_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM applications WHERE id = ?", (application_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)