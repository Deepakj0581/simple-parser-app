from flask import Flask, request, render_template_string
import pandas as pd
from PyPDF2 import PdfReader
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None
    if request.method == "POST":
        file = request.files['file']
        filename = file.filename

        # Validate file type
        if not (filename.endswith(".csv") or filename.endswith(".pdf")):
            error = "Only CSV or PDF files are allowed!"
        else:
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
        {% if error %}
        <p style="color:red;">{{ error }}</p>
        {% endif %}
        {% if result %}
        <h2>Output:</h2>
        <pre style="max-height:300px; overflow:auto; background:#f0f0f0; padding:10px; border-radius:5px;">{{ result | tojson(indent=2) }}</pre>
        {% endif %}
    """, result=result, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
