from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = "jobs.json"
ADMIN_PASSWORD = "admin123"  # You can change this later

# Ensure jobs file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# Load all job postings
def load_jobs():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Save job postings
def save_jobs(jobs):
    with open(DATA_FILE, "w") as f:
        json.dump(jobs, f, indent=4)

# ---------------------------
# ROUTES
# ---------------------------

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

# Route to get all job listings (visible to everyone)
@app.route("/jobs", methods=["GET"])
def get_jobs():
    jobs = load_jobs()
    return jsonify(jobs)

# Route to post a new job (admin only)
@app.route("/jobs", methods=["POST"])
def add_job():
    data = request.get_json()
    password = data.get("password")

    # Check if admin password matches
    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized access"}), 403

    job = {
        "title": data.get("title"),
        "company": data.get("company"),
        "location": data.get("location"),
        "description": data.get("description"),
        "link": data.get("link"),
        "posted_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    jobs = load_jobs()
    jobs.append(job)
    save_jobs(jobs)

    return jsonify({"message": "Job posted successfully", "job": job}), 201


# ---------------------------
# MAIN ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
