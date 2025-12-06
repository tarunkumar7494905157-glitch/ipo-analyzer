from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    score = int(request.form["score"])
    if score >= 80:
        result = "High Probability"
    elif score >= 50:
        result = "Medium Probability"
    else:
        result = "Low Probability"

    return render_template("result.html", result=result, score=score)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
