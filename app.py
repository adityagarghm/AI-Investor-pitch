import os
from flask import Flask, render_template, request

app = Flask(__name__)

# TODO: Add SQLite database initialization (init_db)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit-pitch", methods=["POST"])
def submit_pitch():
    # Grab form inputs
    startup_name = request.form.get("startup_name")
    category = request.form.get("category")
    ask_amount = request.form.get("ask_amount")
    pitch = request.form.get("pitch")

    # Temporary mock feedback until OpenAI integration
    # TODO: Replace with real OpenAI API call
    mock_investors = [
        {"name": "Tech Titan", "invested": True, "feedback": "Solid tech concept."},
        {"name": "Value Queen", "invested": False, "feedback": "Margins are too thin."},
        {"name": "The Maverick", "invested": True, "feedback": "Sounds crazy enough to work."}
    ]

    # TODO: Save submission to SQLite database

    return render_template(
        "index.html", 
        submitted=True, 
        startup_name=startup_name, 
        investors=mock_investors
    )

if __name__ == "__main__":
    app.run(debug=True)