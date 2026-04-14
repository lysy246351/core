import os

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
# CORS(app, origins=["http://search.airstal.com/m/core/index.html"])


API_KEY = os.getenv("API_KEY")

def sprawdz_auth(request):
    return request.headers.get("Authorization") == f"Bearer {API_KEY}"

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def validate_data(data):
    """Validate that `core` starts with C and `polka` starts with A."""
    if not data:
        return False, "Brak danych"
    core = data.get("core")
    polka = data.get("polka")
    if not core or not polka:
        return False, "Pola 'core' i 'polka' są wymagane"
    if core[0].upper() != "C":
        return False, "Pole 'core' musi zaczynać się od litery C"
    if polka[0].upper() != "A":
        return False, "Pole 'polka' musi zaczynać się od litery A"
    return True, ""

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS core (
            id SERIAL PRIMARY KEY,
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
    if not sprawdz_auth(request):
        return jsonify({"error": "brak autoryzacji"}), 401
    data = request.json
    valid, msg = validate_data(data)
    if not valid:
        return jsonify({"error": "invalid_data", "message": msg}), 400
    conn = get_conn()
    c = conn.cursor()
    
    # Sprawdź czy rekord już istnieje
    c.execute(
        "SELECT id, ilosc FROM core WHERE core = %s AND polka = %s",
        (data["core"], data["polka"])
    )
    existing = c.fetchone()
    
    if existing:
        new_ilosc = existing[1] + int(data["ilosc"])
        c.execute(
            "UPDATE core SET ilosc = %s WHERE id = %s",
            (new_ilosc, existing[0])
        )
    else:
        c.execute(
            "INSERT INTO core (core, polka, ilosc) VALUES (%s, %s, %s)",
            (data["core"], data["polka"], data["ilosc"])
        )
    
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/dane", methods=["GET"])
def pobierz_dane():
    if not sprawdz_auth(request):
        return jsonify({"error": "brak autoryzacji"}), 401
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, core, polka, ilosc FROM core ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

@app.route("/wyczysc", methods=["POST"])
def wyczysc():
    if not sprawdz_auth(request):
        return jsonify({"error": "brak autoryzacji"}), 401
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM core")
    conn.commit()
    conn.close()
    return jsonify({"status": "wyczyszczono"})

@app.route("/edytuj", methods=["POST"])
def edytuj():
    if not sprawdz_auth(request):
        return jsonify({"error": "brak autoryzacji"}), 401
    data = request.json
    valid, msg = validate_data(data)
    if not valid:
        return jsonify({"error": "invalid_data", "message": msg}), 400
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE core
        SET core = %s, polka = %s, ilosc = %s
        WHERE id = %s
    """, (data["core"], data["polka"], data["ilosc"], data["id"]))
    conn.commit()
    conn.close()
    return jsonify({"status": "zaktualizowano"})

@app.route("/usun", methods=["POST"])
def usun():
    if not sprawdz_auth(request):
        return jsonify({"error": "brak autoryzacji"}), 401
    data = request.json
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM core WHERE id = %s", (data["id"],))
    conn.commit()
    conn.close()
    return jsonify({"status": "usunieto"})

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)