from flask import Flask, render_template, request

app = Flask(__name__)

def to_float(name):
    """Form se value leke float bana dega, galti par 0.0 dega"""
    raw = request.form.get(name, "").replace(",", "").strip()
    try:
        return float(raw)
    except ValueError:
        return 0.0

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    # ------- Raw inputs -------
    revenue = to_float("revenue")                # e.g. 1200
    profit = to_float("profit")                  # e.g. 150
    total_assets = to_float("total_assets")      # e.g. 500
    total_liabilities = to_float("total_liabilities")
    debt_ratio_input = to_float("debt_ratio")    # e.g. 30 (percent)
    demand_times = to_float("subscription_demand")  # e.g. 10 (10x)
    sector = request.form.get("sector", "").lower()

    # ------- 1) Profit margin (0–2) -------
    if revenue > 0:
        profit_margin = (profit / revenue) * 100   # %
    else:
        profit_margin = 0

    if profit_margin >= 20:
        profit_score = 2.0
    elif profit_margin >= 10:
        profit_score = 1.0
    elif profit_margin > 0:
        profit_score = 0.5
    else:
        profit_score = 0.0

    # ------- 2) Demand score (0–2) -------
    # demand_times = kitna x subscribe hua (1x, 5x, 15x...)
    if demand_times >= 20:
        demand_score = 2.0
    elif demand_times >= 10:
        demand_score = 1.5
    elif demand_times >= 5:
        demand_score = 1.0
    elif demand_times >= 1:
        demand_score = 0.5
    else:
        demand_score = 0.0

    # ------- 3) Debt score (0–2) -------
    # debt_ratio_input percent me: 20, 35, 60...
    if debt_ratio_input <= 20:
        debt_score = 2.0
    elif debt_ratio_input <= 40:
        debt_score = 1.0
    elif debt_ratio_input <= 60:
        debt_score = 0.5
    else:
        debt_score = 0.0

    # ------- 4) Assets vs Liabilities (0–2) -------
    net_assets = total_assets - total_liabilities
    if total_assets > 0:
        net_ratio = (net_assets / total_assets) * 100
    else:
        net_ratio = 0

    if net_ratio >= 40:
        asset_score = 2.0
    elif net_ratio >= 20:
        asset_score = 1.5
    elif net_ratio > 0:
        asset_score = 1.0
    else:
        asset_score = 0.0

    # ------- 5) Sector strength (0–2) -------
    if any(s in sector for s in ["it", "tech", "pharma"]):
        sector_score = 2.0
    elif any(s in sector for s in ["fmcg", "consumer"]):
        sector_score = 1.5
    elif any(s in sector for s in ["bank", "finance"]):
        sector_score = 1.0
    else:
        sector_score = 0.5 if sector else 0.0

    # ------- Total 0–10 -------
    raw_score = profit_score + demand_score + debt_score + asset_score + sector_score
    score_10 = round(max(0.0, min(10.0, raw_score)), 1)   # clamp 0–10

    # ------- Label -------
    if score_10 >= 7.5:
        result = "High Probability"
    elif score_10 >= 4.0:
        result = "Medium Probability"
    else:
        result = "Low Probability"

    return render_template(
        "result.html",
        result=result,
        score=score_10
    )

if __name__ == "__main__":
    app.run(debug=True)
