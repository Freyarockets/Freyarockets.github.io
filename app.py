import threading
import os
import csv
from flask import Flask, request, send_from_directory, redirect, url_for, render_template_string, jsonify
from pathlib import Path

# Import the processing function from the existing Imgrecog.py
# This file must already exist in the repository root.
from Imgrecog import process_images_with_reporting

app = Flask(__name__)

# Paths used by Imgrecog.py (keeps defaults)
INPUT_DIR = Path("./trajectory")
OUTPUT_DIR = Path("./trajectory_results")
CSV_PATH = OUTPUT_DIR / "detection_report.csv"

# Runtime status
processing_thread = None
processing_lock = threading.Lock()
processing_status = {
    "running": False,
    "last_started": None,
    "last_finished": None,
    "message": "Idle"
}

HOME_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Image Detection Host</title>
  </head>
  <body>
    <h1>Image Detection - Flask Host</h1>
    <p>Status: <strong>{{ status }}</strong></p>
    <form action="/run" method="post">
      <button type="submit">Run Detection Now</button>
    </form>

    <h2>Upload Images</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
      <input type="file" name="files" multiple accept="image/*">
      <button type="submit">Upload</button>
    </form>

    <h2>Results</h2>
    <p><a href="/results">View results and annotated images</a></p>
    <p><a href="/download_csv">Download CSV report</a></p>

    <p>Notes:</p>
    <ul>
      <li>Uploaded images are placed into the <code>trajectory/</code> folder.</li>
      <li>Annotated images and the CSV are saved under <code>trajectory_results/</code>.</li>
      <li>The YOLO model weights (yolov8n.pt) will be used by Imgrecog; ensure ultralytics can access or download them.</li>
    </ul>
  </body>
</html>
"""


def run_processing_background():
    global processing_status
    try:
        with processing_lock:
            processing_status["running"] = True
            processing_status["message"] = "Processing started"
        process_images_with_reporting()
        with processing_lock:
            processing_status["message"] = "Processing finished successfully"
    except Exception as e:
        with processing_lock:
            processing_status["message"] = f"Error: {e}"
    finally:
        with processing_lock:
            processing_status["running"] = False


@app.route("/")
def home():
    status = processing_status.get("message", "Idle")
    return render_template_string(HOME_HTML, status=status)


@app.route("/run", methods=["POST"])
def run_now():
    global processing_thread
    with processing_lock:
        if processing_status.get("running"):
            return "Processing already running", 409
        processing_status["running"] = True
        processing_status["last_started"] = True
        processing_status["message"] = "Queued"

    processing_thread = threading.Thread(target=run_processing_background, daemon=True)
    processing_thread.start()
    return redirect(url_for("home"))


@app.route("/results")
def results():
    # Ensure output dir exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    images = []
    for p in sorted(OUTPUT_DIR.iterdir()):
        if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}:
            images.append(p.name)

    csv_rows = []
    if CSV_PATH.exists():
        try:
            with open(CSV_PATH, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for r in reader:
                    csv_rows.append(r)
        except Exception as e:
            csv_rows = [["Error reading CSV", str(e)]]

    html = ['<h1>Results</h1>']
    html.append(f'<p>Status: <strong>{processing_status.get("message","Idle")}</strong></p>')
    html.append('<h2>Annotated Images</h2>')
    if images:
        for img in images:
            html.append(f'<div><a href="/annotated/{img}"><img src="/annotated/{img}" style="max-height:200px"></a><p>{img}</p></div>')
    else:
        html.append('<p>No annotated images found.</p>')

    html.append('<h2>CSV Report (first 200 lines)</h2>')
    if csv_rows:
        html.append('<table border="1" cellpadding="4">')
        for i, row in enumerate(csv_rows):
            if i > 200:
                html.append('<tr><td>... (truncated)</td></tr>')
                break
            html.append('<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>')
        html.append('</table>')
    else:
        html.append('<p>No CSV report found.</p>')

    html.append('<p><a href="/">Back</a></p>')
    return '\n'.join(html)


@app.route('/annotated/<path:filename>')
def annotated(filename):
    # Serve annotated images from the output directory
    return send_from_directory(str(OUTPUT_DIR.resolve()), filename)


@app.route('/download_csv')
def download_csv():
    if not CSV_PATH.exists():
        return "CSV not found", 404
    return send_from_directory(str(OUTPUT_DIR.resolve()), CSV_PATH.name, as_attachment=True)


@app.route('/upload', methods=['POST'])
def upload():
    # Ensure input directory exists
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = request.files.getlist('files')
    if not files:
        return 'No files uploaded', 400

    saved = []
    for f in files:
        filename = f.filename
        target = INPUT_DIR / filename
        f.save(str(target))
        saved.append(filename)

    return jsonify({'saved': saved})


if __name__ == '__main__':
    # Create dirs if missing
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Run Flask
    app.run(host='0.0.0.0', port=5000, debug=True)
