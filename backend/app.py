import os
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("POSTGRES_DB", "mojabaza")
DB_USER = os.environ.get("POSTGRES_USER", "student")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "sekret")

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn
    
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                task TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Tabela 'todos' gotowa.")
    except Exception as e:
        print(f"Błąd inicjalizacji bazy: {e}")

init_db()

@app.route('/')
def hello():
    return jsonify({"message": "Witaj z kontenera Backend!"})

@app.route('/todos', methods=['GET'])
def get_dotos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, task, completed FROM todos ORDER BY id DESC;')
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    
    tasks_list = [{"id": t[0], "task": t[1], "completed": t[2]} for t in tasks]
    return jsonify(tasks_list)

@app.route('/todos', methods=['POST'])
def add_todo():
    new_task = request.json.get('task')
    if not new_task:
        return jsonify({"error": "Brak treści zadania"}), 400
        
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO todos (task) VALUES (%s) RETURNING id;', (new_task,))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"id": new_id, "task": new_task, "completed": False}), 201

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM todos WHERE id = %s RETURNING id;', (todo_id,))
    deleted_id = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    if deleted_id:
        return jsonify({"message": "Usunięto", "id": todo_id}), 200
    else:
        return jsonify({"error": "Nie znaleziono zadania"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)