from flask import Flask, render_template, request, redirect, send_file, session, url_for
import pandas as pd
import os
from datetime import datetime
import qrcode

# Ensure working directory is correct
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

app = Flask(__name__)
app.secret_key = "supersecret"

EXCEL_FILE = "issues.xlsx"

# Admin credentials
ADMIN_ID = "admin"
ADMIN_PASS = "1234"

# Ensure Excel file exists
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["Name", "Room", "Issue", "Date", "IP"])
    df.to_excel(EXCEL_FILE, index=False)

# Generate QR Code
def generate_qr(url):
    img = qrcode.make(url)
    qr_path = os.path.join("static", "form_qr.png")
    img.save(qr_path)
    return "form_qr.png"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    room = request.form.get("room")
    issue = request.form.get("issue")
    ip = request.remote_addr
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df = pd.read_excel(EXCEL_FILE)
    new_entry = {"Name": name, "Room": room, "Issue": issue, "Date": date, "IP": ip}
    df = df._append(new_entry, ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

    return redirect("/thankyou")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@app.route("/dashboard_teacher")
def dashboard_teacher():
    return render_template("teacher.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uid = request.form.get("userid")
        pwd = request.form.get("password")
        if uid == ADMIN_ID and pwd == ADMIN_PASS:
            session["admin"] = True
            return redirect("/dashboard_admin")
        else:
            return "<h3 style='color:red;'>❌ Invalid credentials</h3><a href='/login'>Try Again</a>"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dashboard_admin")
def dashboard_admin():
    if not session.get("admin"):
        return render_template("no_access.html")
    df = pd.read_excel(EXCEL_FILE)
    return render_template("dashboard.html", data=df.to_dict(orient="records"), admin=True)

@app.route("/download")
def download():
    if not session.get("admin"):
        return render_template("no_access.html")
    return send_file(EXCEL_FILE, as_attachment=True)

@app.route("/clear")
def clear():
    if not session.get("admin"):
        return render_template("no_access.html")
    df = pd.DataFrame(columns=["Name", "Room", "Issue", "Date", "IP"])
    df.to_excel(EXCEL_FILE, index=False)
    return redirect("/dashboard_admin")

if __name__ == "__main__":
    # Detect environment (local vs Render)
    public_url = os.environ.get("RENDER_EXTERNAL_URL")
    if public_url:
        # On Render, use public URL for QR
        qr_file = generate_qr(public_url)
        print(f"\n 🌍 Public server: {public_url}")
    else:
        # Local development
        local_ip = "192.168.1.9"
        url = f"http://{local_ip}:5000"
        qr_file = generate_qr(url)
        print(f"\n 🚀 Local server: {url}")

    print(f"📲 QR Code generated at: static/{qr_file}")
    app.run(debug=True, host="0.0.0.0", port=5000)
