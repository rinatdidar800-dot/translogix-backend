from flask import Flask, render_template, request, redirect
import sqlite3
import requests

app = Flask(__name__)

# ------------------- WhatsApp (Green-API) -------------------
GREEN_ID_INSTANCE = "7103533645"
GREEN_API_TOKEN = "2a9686cbd6ba42cb87ef908305a467cbc6cea6b1fc11464aac"
WHATSAPP_ADMIN = "77761546797"

# ------------------- WhatsApp -------------------
def send_whatsapp(name, phone, message):
    text = (
        "Новая заявка\n\n"
        f"Маршрут: Алматы – Балхаш – Караганда – Астана\n"
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Груз: {message}"
    )

    url = f"https://api.green-api.com/waInstance{GREEN_ID_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"
    payload = {
        "chatId": f"{WHATSAPP_ADMIN}@c.us",
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
            message TEXT
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
    name      = request.form.get("name", "").strip()
    phone     = request.form.get("phone", "").strip()
    message   = request.form.get("message", "").strip()

    if not all([name, phone, message]):
        return "❌ Все поля обязательны!", 400

    try:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO applications (name, phone, message)
                VALUES (?, ?, ?)
            """, (name, phone, message))
            conn.commit()
    except Exception as e:
        print(f"Ошибка базы: {e}")
        return "❌ Ошибка сохранения заявки", 500

    try:
        send_whatsapp(name, phone, message)
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