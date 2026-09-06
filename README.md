# MerchantIQ — AI-Powered Merchant & Product Risk Engine

Competition prototype for the **TVS Credit EPIC IT Case Study — Problem G: Intelligent Merchant & Product Risk Engine**.

## What it does

MerchantIQ continuously combines:

- Live regional weather from Open-Meteo
- Live public product catalogue data from Fake Store API
- Simulated merchant transaction telemetry
- Explainable risk scoring
- Merchant risk ranking
- Product risk scoring
- Anomaly/fraud-style signals
- Early-warning alerts
- Action recommendations

> Important: TVS Credit private merchant/customer data is not publicly available. This prototype therefore uses public APIs for live external signals and clearly labelled simulated transaction telemetry. Do not present the simulated data as TVS data.

## Run locally

Python 3.11 or 3.12 is recommended.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit.

## APIs

### Open-Meteo
Current weather is fetched from:
https://api.open-meteo.com/v1/forecast

No API key is required for the prototype's non-commercial use.

### Fake Store API
A public product catalogue is fetched from:
https://fakestoreapi.com/products

If this API is unavailable, the app still runs because the product catalogue is not essential to the scoring engine.

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository, e.g. `merchant-iq-tvs-credit`.
2. Upload the contents of this folder to the repository.
3. Open https://share.streamlit.io/
4. Sign in with GitHub.
5. Click **Create app**.
6. Select your repository, branch `main`, and entrypoint `app.py`.
7. Click **Deploy**.
8. Share the resulting `*.streamlit.app` URL.

No secrets are required for the current version.

## Demo flow for judges

1. Open the dashboard.
2. Point out the **LIVE** indicator.
3. Show the live weather metrics.
4. Open **Portfolio** and sort by risk.
5. Open **Alerts** and explain why the highest-risk merchant was flagged.
6. Open **Products** to show product-level risk.
7. Open **Merchant deep-dive**.
8. Explain that the model is not a black box: every score has contributing signals and a recommended intervention.
9. Refresh the app to show the external API integration.

## Suggested presentation wording

"We are not claiming access to TVS Credit's confidential customer or merchant systems. Instead, MerchantIQ demonstrates the proposed architecture using publicly accessible real-time signals and a representative transaction telemetry layer. In production, that telemetry layer would be replaced by TVS Credit's authorised LMS, transaction and merchant data feeds."

## Folder structure

```text
merchant-iq/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
└── src/
    ├── __init__.py
    ├── data_api.py
    └── risk_engine.py
```
