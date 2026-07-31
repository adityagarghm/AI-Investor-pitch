import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from groq import Groq

load_dotenv() #gets the env password without me having to compromise it

app = Flask(__name__)
DB_NAME = "pitches.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor() # execuates the actions on the db
    #create a db if it doesn't already exist 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pitches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            startup_name TEXT NOT NULL,
            category TEXT NOT NULL,
            pitch TEXT NOT NULL,
            ask_amount REAL NOT NULL,
            ask_equity REAL NOT NULL,
            valuation REAL NOT NULL,
            investor_responses TEXT NOT NULL,
            total_raised REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row #returns as dict instead of tuple
    return conn


def analyze_pitch_with_ai(startup_name, category, pitch, ask_amount, ask_equity, valuation):    
    api_key = os.getenv("GROQ_API_KEY")
    # Local reponses if key is missing
    if not api_key:
        return [
            {"name": "Tech Titan", "invested": True, "offer": ask_amount * 0.5, "rating": "8/10", "feedback": "Great technical potential"},
            {"name": "Value Queen", "invested": False, "offer": 0, "rating": "4/10", "feedback": "Margins are too thin"},
            {"name": "The Maverick", "invested": True, "offer": ask_amount * 0.5, "rating": "9/10", "feedback": "Wild idea, I'm in"}
        ]

    client = Groq(api_key=api_key)
    #use groq as the backbone AI and then prompt it 
    prompt = f""" 
    Evaluate this startup pitch as 3 distinct Shark Tank investor personas:
    1. Tech Titan (Scalability and tech focused)
    2. Value Queen (Profit margins & valuation focused, they should heavily critique bad valuations!)
    3. The Maverick (Risky, wild, eccentric ideas)

    Startup Name: {startup_name}
    Category: {category}
    Pitch: {pitch}
    Investment Ask: ${ask_amount} for {ask_equity}% equity.
    Implied Company Valuation: ${valuation:,.2f}

    Respond ONLY in valid JSON format.
    Return a JSON object containing a key "investors" with an array of 3 objects with keys:
    - "name": string
    - "invested": boolean
    - "offer": number (dollar amount offered, 0 if not invested)
    - "rating": string (e.g., "7/10")
    - "feedback": string (roast-style funny feedback, especially addressing the valuation)
    """

    try:
        response = client.chat.completions.create( #trying the AI (llama)
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        if not isinstance(data, dict):
            return data

        if "investors" in data:
            return data["investors"]

        return list(data.values())[0]

    except Exception as e:
        print(f"Error calling Groq API: {e}") #if the API isn't working 
        return [
            {"name": "Tech Titan", "invested": False, "offer": 0, "rating": "5/10", "feedback": "API connection error."},
            {"name": "Value Queen", "invested": False, "offer": 0, "rating": "5/10", "feedback": "Connection issue evaluating pitch."},
            {"name": "The Maverick", "invested": False, "offer": 0, "rating": "5/10", "feedback": "Try submitting again!"}
        ]


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit-pitch", methods=["POST"])
def submit_pitch():
    startup_name = request.form.get("startup_name")
    category = request.form.get("category")
    pitch = request.form.get("pitch")
    ask_amount = float(request.form.get("ask_amount", 0))
    ask_equity = float(request.form.get("ask_equity", 1)) # Default to 1 to prevent division by zero
    valuation = ask_amount / (ask_equity / 100)

    investors = analyze_pitch_with_ai(startup_name, category, pitch, ask_amount, ask_equity, valuation)
    total_raised = 0
    for investor in investors:
        if investor.get("invested"):
            total_raised += investor.get("offer", 0)

    conn = get_db_connection()
    cursor = conn.cursor()
    pitch_data = { # storing the data into the column names 
        "startup_name": startup_name,
        "category": category,
        "pitch": pitch,
        "ask_amount": ask_amount,
        "ask_equity": ask_equity,
        "valuation": valuation,
        "investor_responses": json.dumps(investors),
        "total_raised": total_raised
    }
    # putting the data into the db 
    cursor.execute("""INSERT INTO pitches (startup_name, category, pitch, ask_amount, ask_equity, valuation, investor_responses, total_raised) 
                   VALUES (:startup_name, :category, :pitch, :ask_amount, :ask_equity, :valuation, :investor_responses, :total_raised)""", pitch_data)
    pitch_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return redirect(url_for("results", pitch_id=pitch_id)) #takes user to the results page for that specific pitch

@app.route("/results/<int:pitch_id>")
def results(pitch_id):
    conn = get_db_connection()
    query = "SELECT * FROM pitches WHERE id = ?"
    cursor = conn.execute(query, (pitch_id,))
    pitch_data = cursor.fetchone()
    conn.close()

    if not pitch_data: #if trying to search for a pitch that doesn't yet exist
        return "Pitch not found", 404

    investors = json.loads(pitch_data["investor_responses"])
    return render_template("results.html", pitch=pitch_data, investors=investors)


@app.route("/leaderboard")
def leaderboard():
    conn = get_db_connection()
    
    leaderboard_sql = """
        SELECT * FROM pitches 
        ORDER BY total_raised DESC 
        LIMIT 10
    """
    pitches_raw = conn.execute(leaderboard_sql).fetchall() #top 10 

    chart_sql = """
        SELECT category, SUM(total_raised) AS cat_total 
        FROM pitches 
        GROUP BY category 
        HAVING cat_total > 0
    """
    chart_rows = conn.execute(chart_sql).fetchall() #category totals
    conn.close()

    pitches = []
    for pitch in pitches_raw:
        p_dict = dict(pitch)
        try:
            investors = json.loads(p_dict["investor_responses"])
            ratings = {}
            for inv in investors:
                name = inv.get("name")
                rating = inv.get("rating", "N/A")
                ratings[name] = rating
        except Exception:
            ratings = {}
        
        p_dict["tech_rating"] = ratings.get("Tech Titan", "N/A")
        p_dict["value_rating"] = ratings.get("Value Queen", "N/A")
        p_dict["maverick_rating"] = ratings.get("The Maverick", "N/A")
        pitches.append(p_dict)

    chart_labels = []
    chart_values = []

    for row in chart_rows:
        chart_labels.append(row["category"])
        chart_values.append(row["cat_total"])

    return render_template(
        "leaderboard.html", 
        pitches=pitches, 
        chart_labels=json.dumps(chart_labels), 
        chart_values=json.dumps(chart_values)
    )

@app.route("/sharks")
def meet_the_sharks():
    conn = get_db_connection()
    # Fetch all investor responses from the database
    rows = conn.execute("SELECT investor_responses FROM pitches").fetchall()
    conn.close()

    # Dictionary to hold stats
    shark_stats = {
        "Tech Titan": {"deals": 0, "spent": 0, "icon": "🤖", "style": "border-top: 4px solid #3b82f6;"},
        "Value Queen": {"deals": 0, "spent": 0, "icon": "💸", "style": "border-top: 4px solid #10b981;"},
        "The Maverick": {"deals": 0, "spent": 0, "icon": "🤪", "style": "border-top: 4px solid #f59e0b;"}
    }

    # Loop through every pitch ever submitted
    for row in rows:
        investors = json.loads(row["investor_responses"])
        for inv in investors:
            name = inv.get("name")
            if name in shark_stats and inv.get("invested"):
                shark_stats[name]["deals"] += 1
                shark_stats[name]["spent"] += inv.get("offer", 0)


    for stats in shark_stats.values():
        stats["formatted_spent"] = f"${stats['spent']:,.0f}"

    return render_template("sharks.html", stats=shark_stats)

@app.route("/all-pitches")
def all_pitches():
    conn = get_db_connection()
    # Fetch ALL pitches ordered by creation date (newest first)
    pitches_raw = conn.execute("SELECT * FROM pitches ORDER BY created_at DESC").fetchall()
    conn.close()

    pitches = []
    for pitch in pitches_raw:
        p_dict = dict(pitch)
        try: #same thing as leaderboard except showing more than just top 10 
            investors = json.loads(p_dict["investor_responses"])
            ratings = {}
            for inv in investors:
                name = inv.get("name")
                rating = inv.get("rating", "N/A")
                ratings[name] = rating
        except Exception:
            ratings = {}
        
        p_dict["tech_rating"] = ratings.get("Tech Titan", "N/A")
        p_dict["value_rating"] = ratings.get("Value Queen", "N/A")
        p_dict["maverick_rating"] = ratings.get("The Maverick", "N/A")
        pitches.append(p_dict)

    return render_template("all_pitches.html", pitches=pitches)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)