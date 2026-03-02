import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

DB_PATH = Path(__file__).with_name("todo.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )

init_db()

@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/tasks")
def list_tasks():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, title, done, created_at FROM tasks ORDER BY id DESC"
        ).fetchall()
    tasks = [dict(r) for r in rows]
    # done を 0/1 → bool にしたい場合はここで変換してもOK
    return jsonify(tasks)


@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    with get_conn() as conn:
        cur = conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        task_id = cur.lastrowid
        row = conn.execute(
            "SELECT id, title, done, created_at FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return jsonify(dict(row)), 201


@app.patch("/api/tasks/<int:task_id>")
def toggle_done(task_id: int):
    data = request.get_json(silent=True) or {}
    done = data.get("done")
    if done is None:
        return jsonify({"error": "done is required (true/false)"}), 400

    done_int = 1 if bool(done) else 0

    with get_conn() as conn:
        cur = conn.execute("UPDATE tasks SET done = ? WHERE id = ?", (done_int, task_id))
        if cur.rowcount == 0:
            return jsonify({"error": "not found"}), 404
        row = conn.execute(
            "SELECT id, title, done, created_at FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return jsonify(dict(row))


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id: int):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cur.rowcount == 0:
            return jsonify({"error": "not found"}), 404
    return "", 204


if __name__ == "__main__":
    init_db()
    # DockerでもローカルでもOKな設定
    app.run(host="0.0.0.0", port=7000, debug=True)