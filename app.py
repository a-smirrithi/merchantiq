import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
from datetime import datetime, timezone

from src.data_api import get_weather, get_products
from src.risk_engine import build_merchant_data, score_merchants, score_products

st.set_page_config(
    page_title="TVS Credit | Merchant Risk Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
[data-testid="stMetricValue"] {font-size: 1.65rem;}
.risk-card {
    padding: 18px 20px; border-radius: 16px; border: 1px solid rgba(128,128,128,.25);
    background: linear-gradient(135deg, rgba(90,100,180,.10), rgba(30,180,150,.06));
}
.alert-card {
    padding: 14px 18px; border-radius: 12px; border-left: 5px solid #ff4b4b;
    background: rgba(255,75,75,.08);
}
.small {color:#7d8590;font-size:.86rem}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.markdown("## 🛡️ MerchantIQ")
st.sidebar.caption("Real-time merchant & product risk intelligence")
st.sidebar.divider()

city = st.sidebar.selectbox(
    "Risk region",
    ["Chennai", "Bengaluru", "Hyderabad", "Mumbai", "Delhi", "Kolkata", "Pune", "Coimbatore"],
    index=0,
)
refresh = st.sidebar.button("🔄 Refresh live data", width="stretch")
st.sidebar.divider()
st.sidebar.caption("Prototype • TVS Credit EPIC IT Case Study")
st.sidebar.caption("Uses public APIs + simulated transaction telemetry. No private customer data.")

# ---------- Live APIs ----------
try:
    weather = get_weather(city)
    products = get_products()
    api_ok = True
except Exception as e:
    api_ok = False
    weather = {"temperature": 0, "precipitation": 0, "weather_code": 0, "wind_speed": 0, "label": "Unavailable"}
    products = []

merchants = build_merchant_data(city, weather, products)
merchant_scores = score_merchants(merchants)
product_scores = score_products(merchants)

# ---------- Header ----------
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown("# MerchantIQ")
    st.markdown("### AI-powered merchant & product risk intelligence")
    st.caption("Continuous monitoring of portfolio behaviour, regional signals and suspicious activity.")
with c2:
    status = "🟢 LIVE" if api_ok else "🟠 DEMO FALLBACK"
    st.markdown(f"**{status}**")
    st.caption(datetime.now(timezone.utc).strftime("Updated %d %b %Y • %H:%M UTC"))

if not api_ok:
    st.warning("One or more public APIs were unavailable. The dashboard is using deterministic fallback data so the demo remains functional.")

# ---------- KPI row ----------
portfolio = merchant_scores["risk_score"].mean()
high_risk = int((merchant_scores["risk_score"] >= 70).sum())
critical = int((merchant_scores["risk_score"] >= 85).sum())
avg_return = merchants["return_rate"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Portfolio Risk", f"{portfolio:.0f}/100")
k2.metric("High-risk merchants", high_risk, delta=f"{critical} critical")
k3.metric("Avg. return rate", f"{avg_return:.1f}%")
k4.metric("Regional weather", weather["label"])

st.divider()

# ---------- Live environment ----------
st.markdown("## 🌐 Live regional intelligence")
a, b, c, d = st.columns(4)
a.metric("Temperature", f"{weather['temperature']:.1f} °C")
b.metric("Precipitation", f"{weather['precipitation']:.1f} mm")
c.metric("Wind", f"{weather['wind_speed']:.1f} km/h")
d.metric("Weather risk", "HIGH" if weather["precipitation"] > 8 else "MEDIUM" if weather["precipitation"] > 2 else "LOW")

st.caption("Weather is fetched live from Open-Meteo. Merchant transactions are simulated for the competition prototype.")

# ---------- Main tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Portfolio", "🚨 Alerts", "🛍️ Products", "🔍 Merchant deep-dive"])

with tab1:
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("### Merchant risk leaderboard")
        view = merchant_scores[[
            "merchant", "category", "orders", "return_rate", "cancel_rate",
            "rating", "anomaly_score", "risk_score", "risk_level"
        ]].copy()
        view["risk_score"] = view["risk_score"].round(0).astype(int)
        view["return_rate"] = view["return_rate"].round(1)
        view["cancel_rate"] = view["cancel_rate"].round(1)
        view["rating"] = view["rating"].round(1)
        view["anomaly_score"] = view["anomaly_score"].round(0).astype(int)
        st.dataframe(
            view.sort_values("risk_score", ascending=False),
            width="stretch", hide_index=True,
            column_config={
                "risk_score": st.column_config.ProgressColumn("Risk", min_value=0, max_value=100, format="%d"),
                "return_rate": st.column_config.NumberColumn("Returns %"),
                "cancel_rate": st.column_config.NumberColumn("Cancel %"),
                "anomaly_score": st.column_config.ProgressColumn("Anomaly", min_value=0, max_value=100),
            },
        )

    with right:
        fig = px.bar(
            merchant_scores.sort_values("risk_score"),
            x="risk_score", y="merchant", orientation="h",
            color="risk_score", range_color=[0,100],
            title="Merchant risk score"
        )
        fig.update_layout(height=430, margin=dict(l=10,r=10,t=50,b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, width="stretch")

with tab2:
    alerts = merchant_scores.sort_values("risk_score", ascending=False).head(6)
    st.markdown("### 🚨 Priority alerts")
    for _, r in alerts.iterrows():
        reasons = r["top_reasons"]
        level = r["risk_level"]
        st.markdown(
            f"""<div class="alert-card">
            <b>{'🔴' if level=='CRITICAL' else '🟠'} {r['merchant']} — {level}</b><br>
            Risk score <b>{r['risk_score']:.0f}/100</b> · {reasons}<br>
            <span class="small">Recommended action: {r['recommendation']}</span>
            </div>""",
            unsafe_allow_html=True,
        )
        st.write("")

with tab3:
    pleft, pright = st.columns([1.3, 1])
    with pleft:
        st.markdown("### Product risk")
        pv = product_scores.copy()
        pv["risk_score"] = pv["risk_score"].round(0).astype(int)
        pv["return_rate"] = pv["return_rate"].round(1)
        pv["cancel_rate"] = pv["cancel_rate"].round(1)
        st.dataframe(
            pv[["product","category","merchant","orders","return_rate","cancel_rate","risk_score","risk_level"]],
            width="stretch", hide_index=True,
            column_config={"risk_score": st.column_config.ProgressColumn("Risk",min_value=0,max_value=100,format="%d")}
        )
    with pright:
        fig2 = px.scatter(
            product_scores, x="return_rate", y="cancel_rate",
            size="orders", color="risk_score", hover_name="product",
            range_color=[0,100], title="Return vs cancellation risk"
        )
        fig2.update_layout(height=420, margin=dict(l=10,r=10,t=50,b=10), coloraxis_showscale=False)
        st.plotly_chart(fig2, width="stretch")

with tab4:
    names = merchant_scores.sort_values("risk_score", ascending=False)["merchant"].tolist()
    selected = st.selectbox("Select merchant", names)
    r = merchant_scores[merchant_scores["merchant"] == selected].iloc[0]
    m = merchants[merchants["merchant"] == selected].iloc[0]

    x1,x2,x3 = st.columns(3)
    x1.metric("Risk score", f"{r['risk_score']:.0f}/100")
    x2.metric("Orders", f"{int(m['orders']):,}")
    x3.metric("Customer rating", f"{m['rating']:.1f} ⭐")

    st.markdown("### Why is this merchant risky?")
    reasons = r["reason_list"]
    for reason in reasons:
        st.write(f"• {reason}")

    st.markdown("### Recommended intervention")
    st.info(r["recommendation"])

    chart_df = pd.DataFrame({
        "Signal": ["Returns", "Cancellations", "Rating risk", "Anomaly", "Regional stress"],
        "Risk contribution": r["contributions"]
    })
    fig3 = px.bar(chart_df, x="Risk contribution", y="Signal", orientation="h", title="Explainable risk contribution")
    fig3.update_layout(height=300, margin=dict(l=10,r=10,t=50,b=10))
    st.plotly_chart(fig3, width="stretch")

# ---------- Footer ----------
st.divider()
st.caption("MerchantIQ is a competition prototype. Public API data is combined with simulated merchant telemetry to demonstrate the proposed risk engine. It is not a real TVS Credit underwriting system.")
