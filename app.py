from flask import Flask, render_template, send_from_directory, request

app = Flask(__name__)


# ---------- Helper : safe float ----------

def to_float(name, default=0.0):
    """
    Form se value float me convert karega.
    Agar user ne galat / empty dala to default use karega.
    """
    raw = request.form.get(name, "").replace(",", "").strip()
    try:
        return float(raw)
    except ValueError:
        return default


# ---------- Home ----------

@app.route("/")
def home():
    return render_template("index.html")


# ---------- robots.txt ----------

@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt", mimetype="text/plain")


# ---------- sitemap.xml ----------

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml", mimetype="application/xml")


# ---------- Prediction Logic (10 columns, 0–2 each) ----------

@app.route("/predict", methods=["POST"])
def predict():
    # 1) Raw inputs
    profit_margin        = to_float("profit_margin")        # %
    revenue_growth       = to_float("revenue_growth")       # %
    net_profit_growth    = to_float("net_profit_growth")    # %
    gmp_trend            = to_float("gmp_trend")            # ₹
    subscription_demand  = to_float("subscription_demand")  # x times
    market_mood_input    = to_float("market_mood")          # -1 / 0 / 1
    debt_ratio           = to_float("debt_ratio")           # %
    valuation_ratio      = to_float("valuation")            # Your PE / Sector PE
    company_age          = to_float("company_age")          # years
    risk_level_input     = to_float("risk_level")           # 1 / 2 / 3

    # ---------- 1) Profit Margin (0–2) ----------
    if profit_margin >= 20:
        profit_score = 2
    elif profit_margin >= 10:
        profit_score = 1
    else:
        profit_score = 0

    # ---------- 2) Revenue Growth (0–2) ----------
    if revenue_growth >= 20:
        revenue_score = 2
    elif revenue_growth >= 5:
        revenue_score = 1
    else:
        revenue_score = 0

    # ---------- 3) Net Profit Growth (0–2) ----------
    if net_profit_growth >= 20:
        net_profit_score = 2
    elif net_profit_growth >= 5:
        net_profit_score = 1
    else:
        net_profit_score = 0

    # ---------- 4) GMP Trend (0–2) ----------
    if gmp_trend >= 100:
        gmp_score = 2
    elif gmp_trend >= 20:
        gmp_score = 1
    else:
        gmp_score = 0

    # ---------- 5) Subscription Demand (0–2) ----------
    if subscription_demand >= 20:
        demand_score = 2
    elif subscription_demand >= 5:
        demand_score = 1
    else:
        demand_score = 0

    # ---------- 6) Market Mood (0–2) ----------
    #   1  = Bullish → 2 points
    #   0  = Neutral → 1 point
    #  -1  = Bearish → 0 point
    if market_mood_input >= 1:
        market_score = 2
    elif market_mood_input >= 0:
        market_score = 1
    else:
        market_score = 0

    # ---------- 7) Debt Ratio (0–2) ----------
    # Low debt better
    if debt_ratio <= 20:
        debt_score = 2
    elif debt_ratio <= 50:
        debt_score = 1
    else:
        debt_score = 0

    # ---------- 8) Valuation (0–2) ----------
    # valuation_ratio = Your PE / Sector PE
    if valuation_ratio <= 0.8:          # cheap vs sector
        valuation_score = 2
    elif valuation_ratio <= 1.2:        # fair
        valuation_score = 1
    else:                               # expensive
        valuation_score = 0

    # ---------- 9) Company Age (0–2) ----------
    if company_age >= 10:
        age_score = 2
    elif company_age >= 3:
        age_score = 1
    else:
        age_score = 0

    # ---------- 10) Risk Level (0–2) ----------
    # 1 = Low, 2 = Medium, 3 = High
    if risk_level_input <= 1:
        risk_score = 2
    elif risk_level_input == 2:
        risk_score = 1
    else:
        risk_score = 0

    # ---------- Total Raw Score (0–20) ----------
    raw_score = (
        profit_score +
        revenue_score +
        net_profit_score +
        gmp_score +
        demand_score +
        market_score +
        debt_score +
        valuation_score +
        age_score +
        risk_score
    )

    # ---------- Convert to 0–10 ----------
    score_10 = round(raw_score / 2.0, 1)  # one decimal

    # ---------- Simple label (optional) ----------
    if score_10 >= 7.5:
        result_label = "High Probability"
    elif score_10 >= 4.0:
        result_label = "Medium Probability"
    else:
        result_label = "Low Probability"

    return render_template(
        "result.html",
        score=score_10,
        result=result_label,
        raw_score=raw_score
    )


if __name__ == "__main__":
    app.run(debug=True)
