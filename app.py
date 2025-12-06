from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Receive form data
        revenue = float(request.form.get("revenue", 0))
        profit = float(request.form.get("profit", 0))
        assets = float(request.form.get("assets", 0))
        liabilities = float(request.form.get("liabilities", 0))
        debt_ratio = float(request.form.get("debt_ratio", 0))
        demand = float(request.form.get("demand", 0))

        # Simple scoring model
        score = 0
        score += revenue
        score += profit * 2
        score += (assets - liabilities)
        score -= debt_ratio * 10
        score += demand * 5

        if score >= 200:
            result = "High Probability"
        elif score >= 100:
            result = "Medium Probability"
        else:
            result = "Low Probability"

        return render_template("result.html", result=result, score=int(score))

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
