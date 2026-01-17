import os
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("POSTGRES_DB", "mojabaza")
DB_USER = os.environ.get("POSTGRES_USER", "user")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "password")

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

@app.route('/init')
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS visitors (id serial PRIMARY KEY, name varchar(50));')
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "Baza gotowa!"})

@app.route('/')
def hello():
    return jsonify({"message": "Witaj z kontenera Backend!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)