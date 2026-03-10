import os
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "v1")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "apppass")


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    return jsonify({"app": "final-task", "version": APP_VERSION}), 200


@app.route("/messages", methods=["POST"])
def create_message():
    data = request.get_json(silent=True) or {}
    content = data.get("content")

    if not content:
        return jsonify({"error": "content is required"}), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (content) VALUES (%s) RETURNING id", (content,))
    msg_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": msg_id, "content": content}), 201


@app.route("/messages", methods=["GET"])
def list_messages():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, content, created_at FROM messages ORDER BY id ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "content": row[1],
            "created_at": row[2].isoformat()
        })

    return jsonify(result), 200


try:
    init_db()
except Exception as e:
    print(f"DB init failed: {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
