import os
from flask import Flask, request, jsonify
import pandas as pd
from PyPDF2 import PdfReader

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Upload CSV or PDF</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">Upload</button>
    </form>
    """

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files['file']
    filename = file.filename
    file.save(filename)

    try:
        transactions = []
        if filename.endswith(".csv"):
            df = pd.read_csv(filename)
            transactions = df.to_dict(orient="records")
        elif filename.endswith(".pdf"):
            reader = PdfReader(filename)
            for page in reader.pages:
                transactions.append(page.extract_text())
        return jsonify(transactions)
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
