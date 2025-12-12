from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    abort,
    send_from_directory,
)


import os
from datetime import datetime

app = Flask(__name__)

from flask_compress import Compress

Compress(app)

@app.route("/")
def home():
    return render_template("index.html")

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    category = db.Column(db.String(50))
    content = db.Column(db.Text)
    author = db.Column(db.String(50))
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)

class SavedIPO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    ipo_name = db.Column(db.String(150))
    score = db.Column(db.Float)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)


# -------- Basic config --------
app.secret_key = os.environ.get("SECRET_KEY", "change-this-in-production")

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "strongpassword")

# -------- Simple blog data (CMS v1 – code se manage) --------
BLOG_POSTS = [
    {
        "slug": "ipo-scoring-framework",
        "title": "IPO Scoring Framework: 10 Inputs, 1 Clear Score",
        "excerpt": "Kaise profit, demand, leverage aur valuation ko combine karke ek clean 0–10 IPO score nikalein.",
        "category": "Guide",
        "read_time": 7,
        "created_at": datetime(2024, 11, 1),
        "hero_tag": "Playbook",
        "content": """
<p>Ye tool ek educational IPO heat-check hai. Real world me IPO listing outcome
hamesha uncertain hota hai, lekin model aapko <strong>structured thinking</strong> deta hai.</p>

<h3>Why 10 inputs?</h3>
<ul>
  <li>Profitability &amp; margins</li>
  <li>Growth momentum</li>
  <li>Balance sheet leverage</li>
  <li>Valuation premium vs sector</li>
  <li>Market mood &amp; risk appetite</li>
</ul>

<p>Har input ko 0–2 points milte hain. Total raw score 0–20, jise
linearly 0–10 scale par map kiya jaata hai.</p>
        """,
    },
    {
        "slug": "ipo-grey-market-gmp-reality-check",
        "title": "Grey Market GMP: Hype vs Reality",
        "excerpt": "GMP sirf sentiment thermometer hai, guaranteed listing profit nahi.",
        "category": "Insight",
        "read_time": 5,
        "created_at": datetime(2024, 11, 5),
        "hero_tag": "Case study",
        "content": """
<p>Grey market premium (GMP) IPO listing ke around demand ka proxy hota hai.
Lekin sirf GMP par decision lena dangerous hai.</p>

<ul>
  <li>Operator groups GMP ko easily manipulate kar sakte hain.</li>
  <li>Fundamentals weak ho to high GMP bhi short-lived ho sakta hai.</li>
  <li>Hum model me GMP ko <strong>sirf 1 input</strong> ke roop me treat karte hain.</li>
</ul>
        """,
    },
    {
        "slug": "risk-management-before-ipo-application",
        "title": "IPO Apply Karne se Pehle Risk Management Checklist",
        "excerpt": "Position sizing, diversification aur exit plan bina – IPO lottery ban jata hai.",
        "category": "Risk",
        "read_time": 6,
        "created_at": datetime(2024, 11, 10),
        "hero_tag": "Risk",
        "content": """
<p>IPO allocation mil jaaye to bhi risk khatam nahi hota. Listing ke baad volatility high hoti hai.</p>

<ol>
  <li>Capital ka fixed % hi IPOs ke liye allocate karein.</li>
  <li>Ek sector me over-concentration avoid karein.</li>
  <li>Listing ke baad stop-loss aur target levels pre-decide karein.</li>
</ol>
        """,
    },
]


def get_blog_or_404(slug: str):
    for post in BLOG_POSTS:
        if post["slug"] == slug:
            return post
    abort(404)


# -------- Helpers --------
def safe_float(value, default=0.0):
    try:
        text = str(value).replace(",", "").strip()
        return float(text) if text != "" else default
    except (TypeError, ValueError):
        return default


def calculate_ipo_score(form_data):
    """
    10 inputs, har ek 0–2 points.
    Raw score: 0–20
    Final score: 0–10 (1 decimal)
    """

    # 1. Profit margin (%)
    profit_margin = safe_float(form_data.get("profit_margin"))
    if profit_margin >= 20:
        profit_score = 2.0
    elif profit_margin >= 10:
        profit_score = 1.5
    elif profit_margin >= 5:
        profit_score = 1.0
    elif profit_margin > 0:
        profit_score = 0.5
    else:
        profit_score = 0.0

    # 2. Revenue growth YoY (%)
    revenue_growth = safe_float(form_data.get("revenue_growth"))
    if revenue_growth >= 30:
        rev_score = 2.0
    elif revenue_growth >= 15:
        rev_score = 1.5
    elif revenue_growth >= 5:
        rev_score = 1.0
    elif revenue_growth > 0:
        rev_score = 0.5
    else:
        rev_score = 0.0

    # 3. Net profit growth YoY (%)
    net_profit_growth = safe_float(form_data.get("net_profit_growth"))
    if net_profit_growth >= 30:
        npg_score = 2.0
    elif net_profit_growth >= 15:
        npg_score = 1.5
    elif net_profit_growth >= 5:
        npg_score = 1.0
    elif net_profit_growth > 0:
        npg_score = 0.5
    else:
        npg_score = 0.0

    # 4. GMP (₹)
    gmp = safe_float(form_data.get("gmp"))
    if gmp >= 200:
        gmp_score = 2.0
    elif gmp >= 100:
        gmp_score = 1.5
    elif gmp >= 50:
        gmp_score = 1.0
    elif gmp > 0:
        gmp_score = 0.5
    else:
        gmp_score = 0.0

    # 5. Total subscription (times)
    subs = safe_float(form_data.get("subscription"))
    if subs >= 50:
        subs_score = 2.0
    elif subs >= 20:
        subs_score = 1.5
    elif subs >= 5:
        subs_score = 1.0
    elif subs > 1:
        subs_score = 0.5
    else:
        subs_score = 0.0

    # 6. Market mood (-1, 0, 1)
    mood = safe_float(form_data.get("market_mood"))
    if mood >= 1:
        mood_score = 2.0
    elif mood >= 0:
        mood_score = 1.0
    else:
        mood_score = 0.5  # bearish environment – tougher listing

    # 7. Debt ratio (% of equity)
    debt_ratio = safe_float(form_data.get("debt_ratio"))
    if debt_ratio <= 20:
        debt_score = 2.0
    elif debt_ratio <= 40:
        debt_score = 1.5
    elif debt_ratio <= 60:
        debt_score = 1.0
    elif debt_ratio <= 80:
        debt_score = 0.5
    else:
        debt_score = 0.0

    # 8. Valuation (PE vs sector)
    valuation = safe_float(form_data.get("valuation_pe"))
    if valuation <= 1.2:
        val_score = 2.0
    elif valuation <= 1.5:
        val_score = 1.5
    elif valuation <= 2.0:
        val_score = 1.0
    elif valuation <= 2.5:
        val_score = 0.5
    else:
        val_score = 0.0

    # 9. Company age (years)
    age = safe_float(form_data.get("company_age"))
    if age >= 10:
        age_score = 2.0
    elif age >= 5:
        age_score = 1.5
    elif age >= 3:
        age_score = 1.0
    elif age > 0:
        age_score = 0.5
    else:
        age_score = 0.0

    # 10. Risk level (1=Low, 2=Med, 3=High)
    risk_level = safe_float(form_data.get("risk_level"))
    if risk_level <= 1:
        risk_score = 2.0
    elif risk_level <= 2:
        risk_score = 1.0
    else:
        risk_score = 0.5  # very high risk → cut some points

    raw_score = (
        profit_score
        + rev_score
        + npg_score
        + gmp_score
        + subs_score
        + mood_score
        + debt_score
        + val_score
        + age_score
        + risk_score
    )

    # Clamp 0–20 and map to 0–10
    raw_score = max(0.0, min(20.0, raw_score))
    score_10 = round((raw_score / 20.0) * 10.0, 1)

    if score_10 >= 7.5:
        label = "High Probability"
        color = "high"
    elif score_10 >= 4.0:
        label = "Medium Probability"
        color = "medium"
    else:
        label = "Low Probability"
        color = "low"

    return score_10, raw_score, label, color


def is_logged_in():
    return session.get("logged_in") is True

# ----- Blog -----
@app.route("/blog")
def blog_list():
    posts = sorted(BLOG_POSTS, key=lambda p: p["created_at"], reverse=True)
    return render_template("blog_list.html", posts=posts)


@app.route("/blog/<slug>")
def blog_detail(slug):
    post = get_blog_or_404(slug)
    return render_template("blog_detail.html", post=post)





# ----- Auth + dashboard (foundation for premium) -----
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["logged_in"] = True
            session["is_admin"] = True
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"

    return render_template("login.html", error=error)



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

def admin_required(f):
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


    # Simple placeholder stats – future me DB se real analytics laa sakta hai
    stats = {
        "total_ipo_runs": 0,
        "avg_score": 0,
        "high_zone_count": 0,
        "medium_zone_count": 0,
        "low_zone_count": 0,
    }
    return render_template("dashboard.html", stats=stats)


# ----- Static SEO files -----
@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml", mimetype="application/xml")


# ----- Error handlers -----
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)

# ========== Admin Login System ==========

from flask import flash

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password) and user.is_admin:
            session["admin_id"] = user.id
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials", "error")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    return redirect(url_for("admin_login"))


# -------- Access protection decorator --------
def admin_required(f):
    def wrap(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap


# -------- Dashboard Route --------
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template("admin_dashboard.html", blogs=blogs)

