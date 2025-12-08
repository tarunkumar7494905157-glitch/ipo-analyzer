from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# ---- Homepage ----
@app.route("/")
def home():
    return render_template("index.html")


# ---- robots.txt serve ----
@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt", mimetype="text/plain")


# ---- sitemap.xml serve ----
@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml", mimetype="application/xml")


# ---- Prediction form ----
@app.route("/predict", methods=["POST"])
def predict():
    revenue = float(request.form.get("revenue", 0))
    profit = float(request.form.get("profit", 0))
    # etc… (your full scoring logic here)
    return render_template("result.html", result="Score calculated")


if __name__ == "__main__":
    app.run()
