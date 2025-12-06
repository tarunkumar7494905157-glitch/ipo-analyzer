from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        company = request.form["company"]
        sector = request.form["sector"]
        issue_size = float(request.form["issue_size"])
        price_band = request.form["price_band"]
        revenue = float(request.form["revenue"])
        profit = float(request.form["profit"])
        assets = float(request.form["assets"])
        liabilities = float(request.form["liabilities"])
        debt_ratio = float(request.form["debt_ratio"])
        subscription = float(request.form["subscription"])
        promoter = float(request.form["promoter"])

        score = 0

        # Financial Strength
        if revenue > 0:
            score += min((revenue / 100) * 10, 20)

        if profit > 0:
            score += min((profit / 50) * 10, 20)

        # Demand
        score += min(subscription * 2, 20)

        # Promoter Holding
        if promoter >= 60:
            score += 20
        elif promoter >= 40:
            score += 10

        # Debt (lower is better)
        if debt_ratio < 0.5:
            score += 20
        elif debt_ratio < 1:
            score += 10

        # Final result category
        if score >= 70:
            result = "High Probability"
        elif score >= 40:
            result = "Medium Probability"
        else:
            result = "Low Probability"

        return render_template(
            "result.html",
            company=company,
            result=result,
            score=int(score)
        )
    
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
