from flask import Flask, request, render_template_string, jsonify
import pandas as pd
from PyPDF2 import PdfReader
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
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
            result = transactions
        finally:
            if os.path.exists(filename):
                os.remove(filename)
    return render_template_string("""
        <h1>Upload CSV or PDF</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Upload</button>
        </form>
        {% if result %}
        <h2>Output:</h2>
        <pre>{{ result | tojson(indent=2) }}</pre>
        {% endif %}
    """, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
