from flask import Flask, request, render_template_string
import pandas as pd
from PyPDF2 import PdfReader
import os
import re

app = Flask(__name__)

def parse_invoice_text(text):
    data = {}

    # Invoice Number
    invoice_match = re.search(r'Invoice\s*#?(\d+)', text)
    if invoice_match:
        data["invoice_number"] = invoice_match.group(1)

    # Date
    date_match = re.search(r'Date:\s*([\d\-]+)', text)
    if date_match:
        data["date"] = date_match.group(1)

    # Customer
    customer_match = re.search(r'Customer:\s*(.+)', text)
    if customer_match:
        data["customer"] = customer_match.group(1).strip()

    # Total
    total_match = re.search(r'Total:\s*(\$?\d+)', text)
    if total_match:
        data["total"] = total_match.group(1)

    return data


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None

    if request.method == "POST":
        file = request.files['file']
        filename = file.filename

        if not (filename.endswith(".csv") or filename.endswith(".pdf")):
            error = "Only CSV or PDF files are allowed!"
        else:
            file.save(filename)
            try:
                if filename.endswith(".csv"):
                    df = pd.read_csv(filename)
                    result = df.to_dict(orient="records")

                elif filename.endswith(".pdf"):
                    reader = PdfReader(filename)
                    full_text = ""

                    for page in reader.pages:
                        full_text += page.extract_text() + "\n"

                    # NEW: structured parsing
                    result = parse_invoice_text(full_text)

            finally:
                if os.path.exists(filename):
                    os.remove(filename)

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Smart Invoice Parser</title>
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Upload Invoice (PDF or CSV)</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">Upload</button>
    </form>
    {% if error %}
    <p class="error">{{ error }}</p>
    {% endif %}
    {% if result %}
    <h2>Parsed Output:</h2>
    <pre>{{ result | tojson(indent=2) }}</pre>
    {% endif %}
</body>
</html>
""", result=result, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
