from flask import Flask, request, render_template_string
import pandas as pd
from PyPDF2 import PdfReader
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None
    is_csv = False
    if request.method == "POST":
        file = request.files['file']
        filename = file.filename

        # Validate file type
        if not (filename.endswith(".csv") or filename.endswith(".pdf")):
            error = "Only CSV or PDF files are allowed!"
        else:
            file.save(filename)
            try:
                if filename.endswith(".csv"):
                    df = pd.read_csv(filename)
                    result = df.to_dict(orient="records")
                    is_csv = True
                elif filename.endswith(".pdf"):
                    reader = PdfReader(filename)
                    pages_text = []
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            # Flatten lines into a single paragraph
                            pages_text.append("\n".join([line.strip() for line in text.splitlines() if line.strip()]))
                    result = pages_text
                    is_csv = False
            finally:
                if os.path.exists(filename):
                    os.remove(filename)

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>File Parser</title>
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Upload CSV or PDF</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">Upload</button>
    </form>

    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}

    {% if result %}
        <h2>Output:</h2>
        {% if is_csv %}
            <table>
                <thead>
                    <tr>
                    {% for col in result[0].keys() %}
                        <th>{{ col }}</th>
                    {% endfor %}
                    </tr>
                </thead>
                <tbody>
                {% for row in result %}
                    <tr>
                    {% for val in row.values() %}
                        <td>{{ val }}</td>
                    {% endfor %}
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        {% else %}
            <div class="pdf-output">
                {% for page in result %}
                    <p>{{ page | replace('\n', '<br>') | safe }}</p>
                    <hr>
                {% endfor %}
            </div>
        {% endif %}
    {% endif %}
</body>
</html>
""", result=result, error=error, is_csv=is_csv)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
