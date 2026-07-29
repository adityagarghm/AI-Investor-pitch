import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)
DB_NAME = "pitches.db"


def init_db():
    #Create the database table if it doesn't exist yet.
    schema = """
    CREATE TABLE IF NOT EXISTS pitches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        startup_name TEXT NOT NULL,
        category TEXT NOT NULL,
        pitch TEXT NOT NULL,
        ask_amount REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(schema)


init_db()


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def get_formatted_pitches():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM pitches ORDER BY id DESC").fetchall()
    conn.close()

    pitches = []
    for row in rows:
        pitches.append({
            "startup_name": row["startup_name"],
            "category": row["category"],
            "pitch": row["pitch"],
            "formatted_ask": f"${row['ask_amount']:,.2f}"
        })
    return pitches


@app.route("/")
def index():
    pitches = get_formatted_pitches()
    return render_template("index.html", pitches=pitches)


@app.route("/submit-pitch", methods=["POST"])
def submit_pitch():

    startup_name = request.form.get("startup_name")
    category = request.form.get("category")
    pitch = request.form.get("pitch")
    ask_amount = float(request.form.get("ask_amount", 0))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pitches (startup_name, category, pitch, ask_amount) VALUES (?, ?, ?, ?)",
        (startup_name, category, pitch, ask_amount)
    )
    conn.commit()
    conn.close()
    pitches = get_formatted_pitches()

    return render_template(
        "index.html",
        pitches=pitches,
        submitted=True,
        startup_name=startup_name
    )


if __name__ == "__main__":
    app.run(debug=True)