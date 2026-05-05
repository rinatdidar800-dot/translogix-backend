from flask import Flask, render_template, request, redirect
import sqlite3
import requests

app = Flask(__name__)

# ------------------- Telegram -------------------
TELEGRAM_TOKEN = "8589944862:AAF91FI_pwX5JoDX6DmZRGGdE5YI_l9RgtU"
TELEGRAM_ADMINS = ["1016799185"]

# ------------------- WhatsApp (Green-API) -------------------
GREEN_ID_INSTANCE = "7103533645"  # без @c.us
GREEN_API_TOKEN = "2a9686cbd6ba42cb87ef908305a467cbc6cea6b1fc11464aac"

# Маршруты → номера админов
WHATSAPP_ROUTES = {
    "astana-almaty": ["77055394342"],
    "almaty-astana": ["77761546797"]
}

# ------------------- Telegram -------------------
def send_telegram(name, phone, message, direction):
    text = (
        f"📦 Новая заявка\n\n"
        f"🛣 Направление: {direction}\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"📝 Сообщение: {message}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for chat_id in TELEGRAM_ADMINS:
        requests.post(url, data={"chat_id": chat_id, "text": text})

# ------------------- WhatsApp -------------------
def send_whatsapp(name, phone, message, direction):
    route_names = {
        "astana-almaty": "Астана - Караганда - Алматы",
        "almaty-astana": "Алматы - Караганда - Астана"
    }

    admins = WHATSAPP_ROUTES.get(direction, [])
    if not admins:
        return

    text = (
        "Новая заявка\n\n"
        f"Маршрут: {route_names.get(direction)}\n"
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

        resp = requests.post(url, json=payload)
        print("WA STATUS:", resp.status_code, resp.text)

# ------------------- База -------------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            message TEXT,
            direction TEXT
        )
    """)
    conn.commit()
    conn.close()

# ------------------- Главная -------------------
@app.route("/")
def home():
    return render_template("index.html")

# ------------------- Отправка формы -------------------
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    phone = request.form.get("phone")
    message = request.form.get("message")
    direction = request.form.get("direction")

    # Проверка обязательных полей
    if not all([name, phone, message, direction]):
        return "❌ Все поля обязательны!", 400

    # Сохраняем в базе
    try:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO applications (name, phone, message, direction)
                VALUES (?, ?, ?, ?)
            """, (name, phone, message, direction))
            conn.commit()
    except Exception as e:
        print(f"Ошибка базы: {e}")
        return "❌ Ошибка сохранения заявки", 500

    # Отправка уведомлений
    try:
        send_telegram(name, phone, message, direction)
    except Exception as e:
        print(f"Ошибка Telegram: {e}")

    try:
        send_whatsapp(name, phone, message, direction)
    except Exception as e:
        print(f"Ошибка WhatsApp: {e}")

    return redirect("/")

# ------------------- Админка -------------------
@app.route("/admin")
def admin():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM applications ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return render_template("admin.html", data=data)

# ------------------- Удаление -------------------
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM applications WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ------------------- Запуск -------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)