from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

DB_FILE = 'todo.db'

# Initialize the SQLite DB
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/todos', methods=['GET'])
def get_todos():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, task, done FROM todos')
    todos = [{'id': row[0], 'task': row[1], 'done': bool(row[2])} for row in c.fetchall()]
    conn.close()
    return jsonify(todos)

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.json
    task = data.get('task', '')
    if not task:
        return jsonify({'error': 'Task is required'}), 400
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO todos (task, done) VALUES (?, ?)', (task, False))
    conn.commit()
    todo_id = c.lastrowid
    conn.close()
    return jsonify({'id': todo_id, 'task': task, 'done': False}), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def toggle_done(todo_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE todos SET done = NOT done WHERE id = ?', (todo_id,))
    conn.commit()
    c.execute('SELECT id, task, done FROM todos WHERE id = ?', (todo_id,))
    row = c.fetchone()
    conn.close()
    return jsonify({'id': row[0], 'task': row[1], 'done': bool(row[2])})

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    return '', 204

if __name__ == '__main__':
    init_db()
    app.run(debug=True)