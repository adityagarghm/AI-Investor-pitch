# AI Shark Tank

> Face the AI Sharks. Pitch your startup to three distinct AI investors powered by the Groq Llama 3 model, secure funding, and climb the leaderboard!


---
## Configure Virtual Local Environment

**Published on the web: https://ai-investor-pitch-production.up.railway.app/**

To run locally: 
1. **Clone the Repository:** Download or clone your project repository to your computer using Git and enter the project folder.

2. **Create & Activate a Virtual Environment:** Open your terminal in that folder, create a Python virtual environment, and activate it. **Mac:** python3 -m venv venv, source venv/bin/activate 
**Windows:** python -m venv venv, venv\Scripts\activate

3. **Install Requirements:** pip install -r requirements.txt to install all the dependencies

4. **Get a Groq API Key:** Head over to console.groq.com, create a free account, and generate an API key.

5. **Set Up Your .env File:** Create a text file named .env in your root directory and save your GROQ_API_KEY value inside it.

6. **Run the App:** Launch app.py using Python in your terminal 
---
## About The Project

**AI Shark Tank** is a full-stack web application built with **Flask**, **SQLite**, and **Groq AI (Llama-3.3-70b)** that simulates the environment of *Shark Tank*. Users submit their startup idea, category, ask amount, equity, and  pitch. Three unique AI investors instantly evaluate the pitch, deliver feedback, provide categorical ratings, and decide whether to invest or say **"You're Out!"**.

### Why It's Interesting & Useful

- **AI Integration:** Uses cutting-edge LLMs via the Groq API to generate highly entertaining investor feedback based on real financial valuations.
- **Interactive Financial Engine:** Calculates implied company valuations and tracks portfolio totals across multiple database-backed models.
- **Data Visualizations:** Contains interactive charts powered by **Chart.js** to break down funding distribution
- **Modern UI:** Designed with **Pico CSS** and custom styling for a dark-mode-first aesthetic.

---

## Key Features

- **The Pitch Room:** Submit your startup details with a real-time character counter and loading states.
- **The AI Sharks:**
  - **🤖 Tech Titan:** Focused on code quality, scalability, and technical architecture.
  - **💸 Value Queen:** Brutally honest about profit margins, realistic valuations, and unit economics.
  - **🤪 The Maverick:** Looking for wild, high-risk gambles.
- **Leaderboard:** Ranks top-funded startups and visualizes category trends using an interactive doughnut chart.
- **Pitch Directory & Search:** Filter through all submitted pitches in real time using a live search bar.
- **Meet the Sharks:** Live statistics tracking total deals closed and capital deployed.
- **Shareable Results:** Copy custom pitch results directly to your clipboard to share with friends.
- **Visibility** Able to view the feedback for all pitches, allowing you to differentiate between the good, the bad, and the best

---

## Tech Stack

- **Backend:** Python, Flask, SQLite (`sqlite3`)
- **AI Engine:** Groq API (`llama-3.3-70b-versatile`)
- **Frontend:** HTML5, Jinja2 Templates, Pico CSS, JavaScript (Chart.js)

---

## 📁 Project Structure

```text
Final-Project/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (Groq API Key)
├── static/
│   └── styles.css         # CSS Styling
└── templates/
    ├── base.html          # Global layout and navbar
    ├── index.html         # Pitch submission form
    ├── results.html       # Investor verdicts 
    ├── leaderboard.html   # Top-funded startups and Chart.js graph
    ├── all_pitches.html   # Searchable pitch directory
    └── sharks.html        # Sharks description and portfolio
