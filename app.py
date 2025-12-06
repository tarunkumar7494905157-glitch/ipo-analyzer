from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.form.to_dict()

    # Convert numeric fields to float
    revenue = float(data["revenue"])
    profit = float(data["profit"])
    assets = float(data["assets"])
    liabilities = float(data["liabilities"])
    debt_ratio = float(data["debt_ratio"])
    demand = float(data["demand"])
    promoter = float(data["promoter_holding"])

    # IPO Scoring Logic
    score = 0

    # Revenue & Profit
    if revenue > 100:
        score += 15
    if profit > 50:
        score += 15

    # Financial Strength
    if assets > liabilities:
        score += 20

    # Low Debt is good
    if debt_ratio < 0.50:
        score += 15

    # Subscription Demand
    if demand > 10:
        score += 20

    # Promoter Holding
    if promoter > 50:
        score += 15

    # Final Probability Category
    if score >= 70:
        result = "High Probability"
    elif score >= 40:
        result = "Medium Probability"
    else:
        result = "Low Probability"

    # RETURN → result.html with variables
    return render_template(
        "result.html",
        company=data["company"],
        result=result,
        score=score
    )


if __name__ == "__main__":
    app.run(debug=True)
