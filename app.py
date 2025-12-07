from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- RESULTS ----------
def to_float(name):
    raw = request.form.get(name, "").replace(",", "").strip()
    try:
        return float(raw)
    except:
        return 0.0

@app.route("/predict", methods=["POST"])
def predict():
    revenue = to_float("revenue")
    profit = to_float("profit")
    total_assets = to_float("total_assets")
    total_liabilities = to_float("total_liabilities")
    debt_ratio_input = to_float("debt_ratio")
    demand_times = to_float("subscription_demand")
    sector = request.form.get("sector", "").lower()

    # Profit score
    if revenue > 0:
        profit_margin = (profit / revenue) * 100
    else:
        profit_margin = 0

    if profit_margin >= 20:
        profit_score = 2
    elif profit_margin >= 10:
        profit_score = 1
    elif profit_margin > 0:
        profit_score = 0.5
    else:
        profit_score = 0

    # Demand score
    if demand_times >= 20:
        demand_score = 2
    elif demand_times >= 10:
        demand_score = 1.5
    elif demand_times >= 5:
        demand_score = 1
    elif demand_times >= 1:
        demand_score = 0.5
    else:
        demand_score = 0

    # Debt score
    if debt_ratio_input <= 20:
        debt_score = 2
    elif debt_ratio_input <= 40:
        debt_score = 1
    elif debt_ratio_input <= 60:
        debt_score = 0.5
    else:
        debt_score = 0

    # Assets score
    net_assets = total_assets - total_liabilities
    if total_assets > 0:
        net_ratio = (net_assets / total_assets) * 100
    else:
        net_ratio = 0

    if net_ratio >= 40:
        asset_score = 2
    elif net_ratio >= 20:
        asset_score = 1.5
    elif net_ratio > 0:
        asset_score = 1
    else:
        asset_score = 0

    # Sector score
    if any(s in sector for s in ["it", "tech", "pharma"]):
        sector_score = 2
    elif any(s in sector for s in ["fmcg", "consumer"]):
        sector_score = 1.5
    elif any(s in sector for s in ["bank", "finance"]):
        sector_score = 1
    else:
        sector_score = 0.5

    raw_score = profit_score + demand_score + debt_score + asset_score + sector_score
    score_10 = round(max(0, min(10, raw_score)), 1)

    if score_10 >= 7.5:
        result = "High Probability"
    elif score_10 >= 4:
        result = "Medium Probability"
    else:
        result = "Low Probability"

    return render_template("result.html", result=result, score=score_10)

# ---------- STATIC FILES ----------

@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt", mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml", mimetype="application/xml")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run()
