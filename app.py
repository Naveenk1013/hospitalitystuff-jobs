from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = "jobs.json"
ADMIN_PASSWORD = "admin123"  # Change this for production

# Ensure jobs file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# Utility functions
def load_jobs():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

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

# Fetch all jobs
@app.route("/jobs", methods=["GET"])
def get_jobs():
    jobs = load_jobs()
    return jsonify(jobs)

# Create new job (admin only)
@app.route("/jobs", methods=["POST"])
def add_job():
    data = request.get_json()
    password = data.get("password")

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


# Update existing job (admin only)
@app.route("/jobs/<int:index>", methods=["PUT"])
def update_job(index):
    data = request.get_json()
    password = data.get("password")

    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized access"}), 403

    jobs = load_jobs()

    if index < 0 or index >= len(jobs):
        return jsonify({"error": "Job not found"}), 404

    # Update job fields
    jobs[index].update({
        "title": data.get("title", jobs[index]["title"]),
        "company": data.get("company", jobs[index]["company"]),
        "location": data.get("location", jobs[index]["location"]),
        "description": data.get("description", jobs[index]["description"]),
        "link": data.get("link", jobs[index].get("link")),
        "updated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    save_jobs(jobs)
    return jsonify({"message": "Job updated successfully", "job": jobs[index]})


# Delete existing job (admin only)
@app.route("/jobs/<int:index>", methods=["DELETE"])
def delete_job(index):
    data = request.get_json()
    password = data.get("password")

    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized access"}), 403

    jobs = load_jobs()

    if index < 0 or index >= len(jobs):
        return jsonify({"error": "Job not found"}), 404

    deleted_job = jobs.pop(index)
    save_jobs(jobs)

    return jsonify({"message": f"Job '{deleted_job['title']}' deleted successfully"})


# ---------------------------
# MAIN ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
