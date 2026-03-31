import os

from flask import Flask, request, jsonify, send_file
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
# CORS(app, origins=["http://search.airstal.com/m/core/index.html"])
DB_FILE = "baza.db"

# API_KEY = os.getenv("API_KEY")

# def sprawdz_auth(request):
#     return request.headers.get("Authorization") == f"Bearer {API_KEY}"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS dane (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            core TEXT,
            polka TEXT,
            ilosc INTEGER
        )
    """)
    conn.commit()
    conn.close()
    
@app.route("/")
def index():
    return send_file("index.html")

@app.route("/dodaj", methods=["POST"])
def dodaj():
    # if not sprawdz_auth(request):
    #     return jsonify({"error": "brak autoryzacji"}), 403
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO dane (core, polka, ilosc) VALUES (?, ?, ?)",
              (data["core"], data["polka"], data["ilosc"]))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/dane", methods=["GET"])
def pobierz_dane():
    # if not sprawdz_auth(request):
    #     return jsonify({"error": "brak autoryzacji"}), 403
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, core, polka, ilosc FROM dane")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

@app.route("/wyczysc", methods=["POST"])
def wyczysc():
    # if not sprawdz_auth(request):
    #     return jsonify({"error": "brak autoryzacji"}), 403
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM dane")
    conn.commit()
    conn.close()
    return jsonify({"status": "wyczyszczono"})

@app.route("/edytuj", methods=["POST"])
def edytuj():
    # if not sprawdz_auth(request):
    #     return jsonify({"error": "brak autoryzacji"}), 403
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE dane
        SET core = ?, polka = ?, ilosc = ?
        WHERE id = ?
    """, (data["core"], data["polka"], data["ilosc"], data["id"]))
    conn.commit()
    conn.close()
    return jsonify({"status": "zaktualizowano"})

@app.route("/usun", methods=["POST"])
def usun():
    # if not sprawdz_auth(request):
    #     return jsonify({"error": "brak autoryzacji"}), 403
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM dane WHERE id = ?", (data["id"],))
    conn.commit()
    conn.close()
    return jsonify({"status": "usunieto"})

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)