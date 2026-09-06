import numpy as np
import pandas as pd
import hashlib

MERCHANTS = [
    ("Nova Electronics", "Electronics"),
    ("Sri Lakshmi Mobiles", "Mobiles"),
    ("Urban Home Hub", "Home"),
    ("Metro Appliances", "Appliances"),
    ("GreenCart Retail", "Grocery"),
    ("Prime Fashion", "Fashion"),
    ("TechZone Outlet", "Electronics"),
    ("CityStyle Store", "Fashion"),
    ("Smart Living", "Home"),
    ("QuickBuy Digital", "Mobiles"),
]

def _rng(city):
    seed = int(hashlib.md5(city.encode()).hexdigest()[:8], 16)
    return np.random.default_rng(seed)

def build_merchant_data(city, weather, products):
    rng = _rng(city)
    rows = []
    weather_stress = min(30, weather["precipitation"] * 1.8 + weather["wind_speed"] * 0.05)

    for i, (name, cat) in enumerate(MERCHANTS):
        orders = int(rng.integers(450, 4800))
        base_return = rng.uniform(3.0, 17.0)
        base_cancel = rng.uniform(2.0, 12.0)
        rating = float(np.clip(rng.normal(4.0, .45), 2.4, 4.9))

        # A deterministic "event" makes a few merchants visibly risky.
        event = 1 if i in [2, 6] else 0
        return_rate = float(np.clip(base_return + event*rng.uniform(5,11), 1, 38))
        cancel_rate = float(np.clip(base_cancel + event*rng.uniform(3,9), 1, 30))
        anomaly = float(np.clip(rng.normal(25, 16) + event*45 + weather_stress*.7, 0, 100))
        fulfilment = float(np.clip(rng.normal(93, 5) - event*10 - weather_stress*.12, 55, 99))

        rows.append({
            "merchant": name, "category": cat, "orders": orders,
            "return_rate": return_rate, "cancel_rate": cancel_rate,
            "rating": rating, "anomaly_score": anomaly,
            "fulfilment": fulfilment, "weather_stress": weather_stress
        })
    return pd.DataFrame(rows)

def score_merchants(df):
    out = df.copy()
    return_risk = np.clip(out["return_rate"] / 25 * 100, 0, 100)
    cancel_risk = np.clip(out["cancel_rate"] / 20 * 100, 0, 100)
    rating_risk = np.clip((5 - out["rating"]) / 2.5 * 100, 0, 100)
    anomaly = out["anomaly_score"]
    fulfilment_risk = np.clip((100 - out["fulfilment"]) / 45 * 100, 0, 100)
    weather = np.clip(out["weather_stress"] * 2.2, 0, 100)

    out["risk_score"] = (
        return_risk*.22 + cancel_risk*.18 + rating_risk*.14 +
        anomaly*.28 + fulfilment_risk*.10 + weather*.08
    ).clip(0,100)

    out["risk_level"] = pd.cut(
        out["risk_score"], [-1, 39, 59, 79, 101],
        labels=["LOW","MEDIUM","HIGH","CRITICAL"]
    ).astype(str)

    def explain(r):
        items, contrib = [], []
        checks = [
            ("High return rate", return_risk.loc[r.name], 18),
            ("Elevated cancellation rate", cancel_risk.loc[r.name], 15),
            ("Low customer rating", rating_risk.loc[r.name], 12),
            ("Suspicious transaction pattern", anomaly.loc[r.name], 25),
            ("Fulfilment degradation", fulfilment_risk.loc[r.name], 10),
            ("Regional weather stress", weather.loc[r.name], 8),
        ]
        for label, value, weight in checks:
            if value >= 55:
                items.append(label)
            contrib.append(round(value * weight / 100, 1))
        if not items:
            items = ["No dominant risk signal; continue routine monitoring."]
        return items, contrib

    explained = out.apply(explain, axis=1)
    out["reason_list"] = [x[0] for x in explained]
    out["contributions"] = [x[1] for x in explained]
    out["top_reasons"] = out["reason_list"].apply(lambda x: ", ".join(x[:3]))

    def rec(level):
        if level == "CRITICAL":
            return "Reduce exposure, trigger enhanced verification and review merchant before new credit."
        if level == "HIGH":
            return "Increase monitoring frequency and temporarily tighten credit/transaction limits."
        if level == "MEDIUM":
            return "Monitor returns, cancellations and fulfilment; review again within 7 days."
        return "Continue normal monitoring and periodic portfolio review."

    out["recommendation"] = out["risk_level"].apply(rec)
    return out

def score_products(merchants):
    rng = _rng("products")
    products = []
    catalog = [
        ("Smartphone", "Mobiles"), ("Laptop", "Electronics"), ("Headphones", "Electronics"),
        ("TV", "Electronics"), ("Kitchen appliance", "Appliances"), ("Shoes", "Fashion"),
        ("Backpack", "Fashion"), ("Home decor", "Home"), ("Mixer", "Appliances"),
        ("Watch", "Fashion"), ("Tablet", "Electronics"), ("Speaker", "Electronics")
    ]
    for i, (product, cat) in enumerate(catalog):
        merchant = merchants.iloc[i % len(merchants)]["merchant"]
        orders = int(rng.integers(120, 1600))
        ret = float(np.clip(rng.normal(9, 5) + (i in [2,8])*8, 1, 32))
        cancel = float(np.clip(rng.normal(6, 3) + (i in [2,8])*5, 1, 24))
        anomaly = float(np.clip(rng.normal(30, 18) + (i in [2,8])*40, 0,100))
        score = float(np.clip(ret/25*35 + cancel/20*25 + anomaly*.40, 0,100))
        products.append({
            "product": product, "category": cat, "merchant": merchant,
            "orders": orders, "return_rate": ret, "cancel_rate": cancel,
            "risk_score": score,
            "risk_level": "CRITICAL" if score>=80 else "HIGH" if score>=60 else "MEDIUM" if score>=40 else "LOW"
        })
    return pd.DataFrame(products)
