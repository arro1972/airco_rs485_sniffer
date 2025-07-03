# rs485_web_parser.py
# Een Flask-webinterface voor het uploaden en analyseren van Home Assistant logs met RS485 hexdata + uploadknop voor ESPHome logs + bestandsoverzicht

from flask import Flask, request, render_template_string, send_file
import re
import csv
import io
import os

app = Flask(__name__)

UPLOAD_FORM = """
<!doctype html>
<title>RS485 Log Analyzer</title>
<h2>Upload je ESPHome/Home Assistant Logbestand</h2>
<form method=post enctype=multipart/form-data>
  <input type=file name=logfile>
  <input type=submit value=Analyseren>
</form>
<br>
<form method=post enctype=multipart/form-data action="/upload">
  <input type=file name=logfile>
  <input type=submit value="Upload logbestand">
</form>
<hr>
<h3>Beschikbare uploads:</h3>
<ul>
{% for fname in files %}
  <li><a href="/analyze/{{ fname }}">{{ fname }}</a></li>
{% endfor %}
</ul>
"""

RESULT_TEMPLATE = """
<!doctype html>
<title>Analyse Resultaten</title>
<h2>Gevonden Wijzigingen in RS485 Bytearrays</h2>
<table border=1 cellpadding=5>
<tr><th>Van</th><th>Naar</th><th>Byte Index</th><th>Oude Waarde</th><th>Nieuwe Waarde</th><th>Functie</th></tr>
{% for row in results %}
<tr>
  <td>{{ row[0] }}</td>
  <td>{{ row[1] }}</td>
  <td>{{ row[2] }}</td>
  <td>{{ row[3] }}</td>
  <td>{{ row[4] }}</td>
  <td>{{ row[5] }}</td>
</tr>
{% endfor %}
</table>
<a href="/download">Download CSV</a>
"""

# Bekende bytefuncties (aanpasbaar)
BYTE_FUNCTIONS = {
    16: "Fan mode",
    17: "Sleep mode",
    18: "Power + AC mode",
    19: "Set temperature",
    23: "Temp comp. (dry mode)",
    32: "ECO / Swing UD",
    33: "Super mode",
    35: "Quiet / ECO / Swing LR",
    36: "LED",
}

analyzed_csv = io.StringIO()

def extract_hex_bytes(line):
    match = re.search(r'((?:[0-9A-Fa-f]{2} )+[0-9A-Fa-f]{2})$', line)
    if match:
        return match.group(1).strip().split()
    return []

def analyze_log(filetext):
    lines = filetext.decode().splitlines()
    entries = [(line[:19], extract_hex_bytes(line)) for line in lines if "debug:RX" in line]
    results = []
    global analyzed_csv
    analyzed_csv = io.StringIO()
    writer = csv.writer(analyzed_csv)
    writer.writerow(["Timestamp From", "Timestamp To", "Byte Index", "Old Value", "New Value", "Function"])

    for i in range(len(entries) - 1):
        t1, b1 = entries[i]
        t2, b2 = entries[i + 1]
        max_len = max(len(b1), len(b2))
        b1 += ['--'] * (max_len - len(b1))
        b2 += ['--'] * (max_len - len(b2))
        for j in range(max_len):
            if b1[j] != b2[j]:
                fn = BYTE_FUNCTIONS.get(j, "Onbekend")
                results.append([t1, t2, j, b1[j], b2[j], fn])
                writer.writerow([t1, t2, j, b1[j], b2[j], fn])

    analyzed_csv.seek(0)
    return results

@app.route('/', methods=['GET', 'POST'])
def upload():
    files = os.listdir("uploads") if os.path.exists("uploads") else []
    if request.method == 'POST':
        file = request.files['logfile']
        if file:
            results = analyze_log(file.read())
            return render_template_string(RESULT_TEMPLATE, results=results)
    return render_template_string(UPLOAD_FORM, files=files)

@app.route('/upload', methods=['POST'])
def upload_logfile():
    file = request.files['logfile']
    if file:
        filepath = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        file.save(filepath)
        return f"✅ Bestand opgeslagen: {filepath}<br><a href='/'>Terug</a>"
    return "❌ Geen bestand ontvangen.<br><a href='/'>Probeer opnieuw</a>"

@app.route('/analyze/<filename>')
def analyze_file(filename):
    path = os.path.join("uploads", filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            results = analyze_log(f.read())
            return render_template_string(RESULT_TEMPLATE, results=results)
    return "❌ Bestand niet gevonden.<br><a href='/'>Terug</a>"

@app.route('/download')
def download():
    return send_file(io.BytesIO(analyzed_csv.getvalue().encode()),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='rs485_byte_differences.csv')

if __name__ == '__main__':
    app.run(debug=True)
