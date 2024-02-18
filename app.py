from flask import Flask, render_template, request, redirect, g
import sqlite3
import random

app = Flask(__name__)

def get_message_db():
    """
    retrieves the message database from the global context (g).
    if does not exist, creates a new database and table.
    returns g.message_db
    """
    try:
        return g.message_db
    except AttributeError:
        g.message_db = sqlite3.connect("messages_db.sqlite")
        cursor = g.message_db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                handle TEXT,
                message TEXT
            )
        ''')
        return g.message_db

def insert_message(request):
    """
    inserts a message from the request form to the "messages" table
    of database. The conn is opened beforehand, then closed.
    returns the handle and message.
    """
    message = request.form['message']
    handle = request.form['username']
    conn = get_message_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (handle, message) VALUES (?, ?)
    ''', (handle, message))
    conn.commit()
    conn.close()
    return handle, message

def random_messages(n):
    """
    connects to the database and selects a random message from
    the database. then the connection is closed.
    inputs "n" - number of messages to select
    returns the randomly selected n number of messages
    """
    conn = sqlite3.connect("messages_db.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT handle, message FROM messages")
    messages = cursor.fetchall()
    conn.close()
    return random.sample(messages, min(n, len(messages)))

def render_view_template():
    """
    calls the random_messages function and renders the
    "view.html" template with the selected messages.
    returns rendered template
    """
    messages = random_messages(5)  # Grabbing up to 5 random messages
    return render_template('view.html', messages=messages)

@app.route('/view')
def view():
    return render_view_template()

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        handle, message = insert_message(request)
        return render_template('submit.html', submitted=True, handle=handle, message=message)
    return render_template('submit.html')

@app.route('/')
def home():
    return "Home Page"

if __name__ == '__main__':
    app.run(debug=True)
