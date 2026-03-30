import os

from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DB_FILE = "baza.db"

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

@app.route("/dodaj", methods=["POST"])
def dodaj():
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
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, core, polka, ilosc FROM dane")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

@app.route("/wyczysc", methods=["POST"])
def wyczysc():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM dane")
    conn.commit()
    conn.close()
    return jsonify({"status": "wyczyszczono"})

@app.route("/edytuj", methods=["POST"])
def edytuj():
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
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM dane WHERE id = ?", (data["id"],))
    conn.commit()
    conn.close()
    return jsonify({"status": "usunieto"})

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)