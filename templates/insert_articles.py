from app import db, BlogPost

posts = [
    BlogPost(
        title="IPO Apply Karne Se Pehle Risk Management Checklist",
        slug="ipo-risk-management-checklist",
        category="Risk",
        read_time=6,
        hero_tag="Risk guide",
        excerpt="Position sizing + exit plan + allocation rules — IPO loss avoid karne ka solid checklist.",
        content="""(Yaha pura Article 1 ka HTML paste karein — main turant de dunga)"""
    ),
    BlogPost(
        title="Grey Market GMP: Hype vs Reality",
        slug="gmp-hype-vs-reality",
        category="Insight",
        read_time=5,
        hero_tag="Case study",
        excerpt="GMP sirf sentiment indicator hai — real listing ka guarantee nahi deta.",
        content="""(Yaha Article 2 ka HTML)"""
    ),
    BlogPost(
        title="IPO Scoring Framework: 10 Inputs, 1 Clear Score",
        slug="ipo-scoring-framework",
        category="Playbook",
        read_time=7,
        hero_tag="Playbook",
        excerpt="Kaise profit, demand, valuation combine karke AI-style clean 0–10 IPO score nikalte hain.",
        content="""(Yaha Article 3 ka HTML)"""
    ),
]

for p in posts:
    db.session.add(p)

db.session.commit()
print("All 3 articles added!")
