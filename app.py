import os
import csv
import pdfplumber
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def parse_csv(filepath):
    transactions = []
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            transactions.append(row)
    return transactions

def parse_pdf(filepath):
    transactions = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                for line in lines:
                    transactions.append(line.split())
    return transactions

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    try:
        if file.filename.lower().endswith(".csv"):
            transactions = parse_csv(filepath)
        elif file.filename.lower().endswith(".pdf"):
            transactions = parse_pdf(filepath)
        else:
            return jsonify({"error": "Unsupported file type"}), 400
        return jsonify({"transactions": transactions})
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == "__main__":
    app.run(debug=True)

