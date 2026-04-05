import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import smtplib
import time
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Stock Alert Dashboard", page_icon="📈", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .metric-card {
        background: linear-gradient(135deg, #1a1f2e, #232a3d);
        border: 1px solid #2e3650; border-radius: 14px;
        padding: 20px 24px; text-align: center; color: white; margin-bottom: 8px;
    }
    .metric-card .label { font-size: 12px; color: #7a8aaa; letter-spacing: 1px; text-transform: uppercase; }
    .metric-card .value { font-size: 26px; font-weight: 600; margin-top: 6px; }
    .green  { color: #36d68a !important; }
    .red    { color: #ff5c5c !important; }
    .blue   { color: #4f8ef7 !important; }
    .yellow { color: #f7c948 !important; }
    .purple { color: #a78bfa !important; }

    .alert-box {
        background: linear-gradient(135deg,#1f2d1f,#243324);
        border: 1.5px solid #36d68a; border-radius: 12px;
        padding: 18px 24px; color: #36d68a; font-weight: 600; font-size: 17px;
        text-align: center; margin: 10px 0;
    }
    .alert-box-warn {
        background: linear-gradient(135deg,#2a2310,#332d14);
        border: 1.5px solid #f7c948; border-radius: 12px;
        padding: 18px 24px; color: #f7c948; font-weight: 600; font-size: 17px;
        text-align: center; margin: 10px 0;
    }
    .pred-card {
        background: linear-gradient(135deg,#1a1230,#1e1535);
        border: 1px solid #4c3f8a; border-radius: 14px;
        padding: 20px 24px; text-align: center; color: white; margin-bottom: 8px;
    }
    .pred-card .label { font-size: 12px; color: #9d8fd4; letter-spacing: 1px; text-transform: uppercase; }
    .pred-card .value { font-size: 24px; font-weight: 600; margin-top: 6px; color: #a78bfa; }
    .pred-card .sub   { font-size: 12px; color: #9d8fd4; margin-top: 4px; }
    .log-box {
        background: #111521; border: 1px solid #2e3650; border-radius: 10px;
        padding: 14px 18px; font-family: 'DM Mono', monospace; font-size: 13px;
        color: #7a8aaa; max-height: 220px; overflow-y: auto;
    }
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg,#4f8ef7,#7b5cf7); color: white !important;
        border: none; border-radius: 10px; font-family: 'DM Sans',sans-serif;
        font-weight: 600; font-size: 15px; width: 100%; transition: opacity 0.2s;
    }
    div[data-testid="stButton"] > button:hover { opacity: 0.85; }
    .stTextInput input, .stNumberInput input {
        background: #1a1f2e !important; color: white !important;
        border: 1px solid #2e3650 !important; border-radius: 8px !important;
        font-family: 'DM Mono', monospace !important;
    }
    section[data-testid="stSidebar"] { background: #111521; border-right: 1px solid #2e3650; }
    section[data-testid="stSidebar"] * { color: #c4cee0 !important; }
    .stApp { background: #0d1117; color: #e6eaf3; }
    h1, h2, h3 { color: #e6eaf3 !important; }
    .stTabs [data-baseweb="tab"] { font-family: 'DM Sans',sans-serif; font-size: 14px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)
def get_current_price(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1d")
        return round(float(data["Close"].iloc[-1]), 2) if not data.empty else None
    except:
        return None

def get_history(symbol, period):
    try:
        df = yf.Ticker(symbol).history(period=period)
        return df if not df.empty else None
    except:
        return None
def draw_chart(symbol, target_price, period):
    df = get_history(symbol, period)
    if df is None:
        return None
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#111521")
    ax.plot(df.index, df["Close"], color="#4f8ef7", linewidth=2, label="Close Price")
    ax.fill_between(df.index, df["Close"], df["Close"].min(), alpha=0.12, color="#4f8ef7")
    if target_price:
        ax.axhline(y=target_price, color="#ff5c5c", linestyle="--",
                   linewidth=1.5, label=f"Target: ₹{target_price:.2f}")
    ax.axhline(y=df["Close"].max(), color="#36d68a", linestyle=":", linewidth=1,
               alpha=0.5, label=f"High: {df['Close'].max():.2f}")
    ax.axhline(y=df["Close"].min(), color="#f7c948", linestyle=":", linewidth=1,
               alpha=0.5, label=f"Low: {df['Close'].min():.2f}")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, color="#7a8aaa", fontsize=10)
    plt.yticks(color="#7a8aaa", fontsize=10)
    ax.set_title(f"{symbol} — Price History", fontsize=14, fontweight="bold",
                 color="#e6eaf3", pad=14)
    ax.set_xlabel("Date", color="#7a8aaa")
    ax.set_ylabel("Price", color="#7a8aaa")
    ax.legend(facecolor="#1a1f2e", edgecolor="#2e3650", labelcolor="#c4cee0", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.15, color="#ffffff")
    for spine in ax.spines.values():
        spine.set_edgecolor("#2e3650")
    plt.tight_layout()
    return fig

def predict_prices(symbol, history_period, forecast_days):
    """
    Linear Regression on historical closing prices.
    Returns: (fig, predictions, future_dates, r2_score)
    All errors are caught and returned as (None, None, None, None).
    """
    try:
        df = get_history(symbol, history_period)
        if df is None or len(df) < 10:
            return None, None, None, None

        closes = df["Close"].values.astype(float).reshape(-1, 1)
        days   = np.arange(len(closes)).reshape(-1, 1)

        # Scale
        scaler_x = MinMaxScaler()
        scaler_y = MinMaxScaler()
        days_scaled   = scaler_x.fit_transform(days)
        closes_scaled = scaler_y.fit_transform(closes)

        # Train
        model = LinearRegression()
        model.fit(days_scaled, closes_scaled)
        r2 = round(float(model.score(days_scaled, closes_scaled)) * 100, 1)

        # In-sample fit line
        fit_scaled = model.predict(days_scaled)
        fit_prices = scaler_y.inverse_transform(fit_scaled).flatten()

        # Future predictions — extend scaler range manually
        future_days_raw = np.arange(len(closes), len(closes) + forecast_days).reshape(-1, 1)
        # Transform using same scaler (works even beyond training range)
        future_scaled   = scaler_x.transform(future_days_raw)
        pred_scaled     = model.predict(future_scaled)
        predictions     = scaler_y.inverse_transform(pred_scaled).flatten()

        # Future dates (skip weekends for realism)
        last_date    = df.index[-1].to_pydatetime().replace(tzinfo=None)
        future_dates = []
        d = last_date
        while len(future_dates) < forecast_days:
            d += timedelta(days=1)
            if d.weekday() < 5:        # Mon–Fri only
                future_dates.append(d)

        # ── Chart ──────────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(13, 5))
        fig.patch.set_facecolor("#0d1117")
        ax.set_facecolor("#111521")

        hist_dates = [d.to_pydatetime().replace(tzinfo=None) for d in df.index]

        # Historical
        ax.plot(hist_dates, df["Close"].values, color="#4f8ef7",
                linewidth=2, label="Historical Price", zorder=3)
        ax.fill_between(hist_dates, df["Close"].values, df["Close"].min(),
                        alpha=0.08, color="#4f8ef7")

        # Trend line over history
        ax.plot(hist_dates, fit_prices, color="#f7c948", linewidth=1.2,
                linestyle="--", alpha=0.7, label="Trend Line (Regression)", zorder=2)

        # Divider
        ax.axvline(x=last_date, color="#4a5568", linestyle=":", linewidth=1.5)
        ymin_val = float(df["Close"].min()) * 0.995
        ax.text(last_date, ymin_val, "  Today", color="#7a8aaa", fontsize=9, va="bottom")

        # Prediction line
        all_pred_dates = [last_date] + future_dates
        all_pred_vals  = [float(df["Close"].values[-1])] + list(predictions)
        ax.plot(all_pred_dates, all_pred_vals, color="#a78bfa",
                linewidth=2.5, label="Predicted Price", zorder=4)
        ax.fill_between(all_pred_dates, all_pred_vals, float(df["Close"].min()),
                        alpha=0.10, color="#a78bfa")

        # Confidence band ±5%
        upper = [v * 1.05 for v in all_pred_vals]
        lower = [v * 0.95 for v in all_pred_vals]
        ax.fill_between(all_pred_dates, lower, upper, alpha=0.07,
                        color="#a78bfa", label="±5% Confidence Band")

        # End-point annotation
        ax.annotate(
            f"  {predictions[-1]:.2f}",
            xy=(future_dates[-1], predictions[-1]),
            color="#a78bfa", fontsize=11, fontweight="bold",
            xytext=(6, 0), textcoords="offset points"
        )

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45, color="#7a8aaa", fontsize=10)
        plt.yticks(color="#7a8aaa", fontsize=10)
        ax.set_title(
            f"{symbol} — Price Prediction  |  Next {forecast_days} trading days  |  R² = {r2}%",
            fontsize=13, fontweight="bold", color="#e6eaf3", pad=14
        )
        ax.set_xlabel("Date", color="#7a8aaa")
        ax.set_ylabel("Price", color="#7a8aaa")
        ax.legend(facecolor="#1a1f2e", edgecolor="#2e3650",
                  labelcolor="#c4cee0", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.12, color="#ffffff")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2e3650")
        plt.tight_layout()

        return fig, list(predictions), future_dates, r2

    except Exception as e:
        st.error(f"Prediction error: {e}")
        return None, None, None, None


# ── Send email ────────────────────────────────────────────────
def send_email(sender, password, receiver, symbol, current, target):
    try:
        subject = f"Stock Alert: {symbol} hit {current}!"
        body = f"""
Hi Investor!

Your stock alert has been triggered.

  Stock    :  {symbol}
  Target   :  {target:.2f}
  Current  :  {current:.2f}
  Status   :  TARGET REACHED ✅

Time to take action!

— Stock Alert Bot
        """
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"]   = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        return True, "Email sent successfully!"
    except smtplib.SMTPAuthenticationError:
        return False, "Auth failed — check your App Password."
    except Exception as e:
        return False, str(e)


# ═════════════════════════════════════════════════════════════
# SESSION STATE
# ═════════════════════════════════════════════════════════════
for key, default in [
    ("monitoring",   False),
    ("logs",         []),
    ("last_price",   None),
    ("alert_fired",  False),
    ("cfg_sender",   ""),
    ("cfg_password", ""),
    ("cfg_receiver", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ═════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Stock Settings")
    symbol = st.text_input(
        "Stock Symbol", value="TCS.NS",
        placeholder="e.g. AAPL  /  TCS.NS  /  RELIANCE.NS"
    ).upper().strip()
    target_price = st.number_input("Target Price", min_value=0.01, value=4000.0, step=1.0)
    period       = st.selectbox("Chart Period", ["5d","1mo","3mo","6mo","1y"], index=1)
    st.markdown("---")
    fetch_btn   = st.button("🔍 Fetch & Monitor")
    refresh_btn = st.button("🔄 Refresh Price Now")
    st.markdown("---")
    st.caption(
        "🇮🇳 Indian stocks: add `.NS` (NSE) or `.BO` (BSE)\n"
        "e.g. TCS.NS · RELIANCE.NS · INFY.NS\n\n"
        "🇺🇸 US stocks: AAPL · TSLA · MSFT"
    )


# ═════════════════════════════════════════════════════════════
# HEADER + TABS
# ═════════════════════════════════════════════════════════════
st.markdown("## 📈 Stock Price Alert Dashboard")
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Dashboard",
    "📉  Price Prediction",
    "📧  Email Setup",
    "🗒️  Activity Log",
])


# ─────────────────────────────────────────────────────────────
# TAB 1 — Dashboard
# ─────────────────────────────────────────────────────────────
with tab1:

    # Handle fetch/refresh
    if fetch_btn or refresh_btn:
        if not symbol:
            st.error("Enter a stock symbol in the sidebar.")
        else:
            with st.spinner(f"Fetching {symbol}..."):
                price = get_current_price(symbol)
            if price is None:
                st.error(f"Could not fetch **{symbol}**. Check the symbol and try again.")
            else:
                st.session_state.last_price  = price
                st.session_state.monitoring  = True
                st.session_state.alert_fired = False
                st.session_state.logs.insert(0,
                    f"[{time.strftime('%H:%M:%S')}] {symbol} → {price:.2f}")
                if price >= target_price:
                    st.session_state.alert_fired = True
                    s = st.session_state.cfg_sender
                    p = st.session_state.cfg_password
                    r = st.session_state.cfg_receiver
                    if s and p and r:
                        ok, result = send_email(s, p, r, symbol, price, target_price)
                        st.session_state.logs.insert(0,
                            f"[{time.strftime('%H:%M:%S')}] Email → "
                            f"{'✅ Sent' if ok else '❌ ' + result}")

    current_price = st.session_state.last_price
    df_hist       = get_history(symbol, period) if symbol else None

    # Metric cards
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        val   = f"{current_price:.2f}" if current_price else "—"
        color = "green" if (current_price and current_price >= target_price) else "blue"
        st.markdown(f"""<div class="metric-card">
            <div class="label">Current Price</div>
            <div class="value {color}">{val}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Target Price</div>
            <div class="value yellow">{target_price:.2f}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        if current_price:
            gap   = target_price - current_price
            color = "green" if gap <= 0 else "red"
            label = f"{abs(gap):.2f}  {'above ✅' if gap <= 0 else 'below'}"
        else:
            label, color = "—", "blue"
        st.markdown(f"""<div class="metric-card">
            <div class="label">Gap to Target</div>
            <div class="value {color}">{label}</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        if df_hist is not None and len(df_hist) > 1:
            chg   = float(df_hist["Close"].iloc[-1]) - float(df_hist["Close"].iloc[0])
            pct   = (chg / float(df_hist["Close"].iloc[0])) * 100
            color = "green" if chg >= 0 else "red"
            val   = f"{'▲' if chg >= 0 else '▼'} {pct:.2f}%"
        else:
            val, color = "—", "blue"
        st.markdown(f"""<div class="metric-card">
            <div class="label">Period Change</div>
            <div class="value {color}">{val}</div>
        </div>""", unsafe_allow_html=True)

    # Alert banner
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.alert_fired:
        st.markdown(f"""<div class="alert-box">
            🚨 ALERT FIRED!&nbsp; {symbol} reached {current_price:.2f} —
            your target of {target_price:.2f} was hit!
        </div>""", unsafe_allow_html=True)
    elif st.session_state.monitoring:
        st.markdown(f"""<div class="alert-box-warn">
            ⏳ Monitoring {symbol}... Target not yet reached.
            Click "Refresh Price Now" to update.
        </div>""", unsafe_allow_html=True)
    else:
        st.info("👈 Enter a stock symbol in the sidebar and click **Fetch & Monitor** to begin.")

    # Price history chart
    st.markdown("<br>", unsafe_allow_html=True)
    if symbol:
        with st.spinner("Loading chart..."):
            fig = draw_chart(symbol, target_price, period)
        if fig:
            st.pyplot(fig)
        else:
            st.warning("No chart data available for this symbol/period.")


# ─────────────────────────────────────────────────────────────
# TAB 2 — Price Prediction
# ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 📉 Price Prediction")
    st.markdown(
        "Uses **Linear Regression** on historical closing prices to forecast future movement. "
        "The **purple line** shows predicted prices. The **R² score** tells you how well the model fits the data."
    )
    st.markdown("---")

    # Controls
    col_p1, col_p2, col_p3 = st.columns([2, 2, 2])
    with col_p1:
        pred_symbol = st.text_input(
            "Stock Symbol",
            value=symbol or "TCS.NS",
            key="pred_sym",
            placeholder="e.g. TCS.NS / AAPL"
        ).upper().strip()
    with col_p2:
        hist_period = st.selectbox(
            "Training Data Period",
            ["1mo", "3mo", "6mo", "1y", "2y"],
            index=2, key="pred_period",
            help="More history gives a better trend line"
        )
    with col_p3:
        forecast_days = st.slider(
            "Forecast Trading Days",
            min_value=5, max_value=60,
            value=20, step=5, key="pred_days"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    run_pred = st.button("🔮 Run Prediction")

    if run_pred:
        if not pred_symbol:
            st.error("Enter a stock symbol first.")
        else:
            with st.spinner(f"Running prediction for {pred_symbol}..."):
                fig, predictions, future_dates, r2 = predict_prices(
                    pred_symbol, hist_period, forecast_days
                )

            if fig is None:
                st.error(
                    f"Could not predict for **{pred_symbol}**. "
                    "Try a longer training period or check the symbol."
                )
            else:
                current = get_current_price(pred_symbol)

                # Safe index helpers
                idx7  = min(6,  len(predictions) - 1)
                idx30 = min(19, len(predictions) - 1)
                pred_7   = float(predictions[idx7])
                pred_30  = float(predictions[idx30])

                # ── Metric cards ───────────────────────────────
                m1, m2, m3, m4 = st.columns(4)

                with m1:
                    # FIX: compute string first, never inside :.2f
                    cur_str = f"{current:.2f}" if current else "—"
                    st.markdown(f"""<div class="pred-card">
                        <div class="label">Current Price</div>
                        <div class="value" style="color:#4f8ef7">{cur_str}</div>
                        <div class="sub">Live market</div>
                    </div>""", unsafe_allow_html=True)

                with m2:
                    chg7  = ((pred_7 - current) / current * 100) if current else 0.0
                    col7  = "#36d68a" if chg7 >= 0 else "#ff5c5c"
                    arr7  = "▲" if chg7 >= 0 else "▼"
                    st.markdown(f"""<div class="pred-card">
                        <div class="label">7-Day Forecast</div>
                        <div class="value">{pred_7:.2f}</div>
                        <div class="sub" style="color:{col7}">{arr7} {abs(chg7):.1f}%</div>
                    </div>""", unsafe_allow_html=True)

                with m3:
                    chg30 = ((pred_30 - current) / current * 100) if current else 0.0
                    col30 = "#36d68a" if chg30 >= 0 else "#ff5c5c"
                    arr30 = "▲" if chg30 >= 0 else "▼"
                    st.markdown(f"""<div class="pred-card">
                        <div class="label">20-Day Forecast</div>
                        <div class="value">{pred_30:.2f}</div>
                        <div class="sub" style="color:{col30}">{arr30} {abs(chg30):.1f}%</div>
                    </div>""", unsafe_allow_html=True)

                with m4:
                    r2_color = "#36d68a" if r2 >= 80 else "#f7c948" if r2 >= 50 else "#ff5c5c"
                    st.markdown(f"""<div class="pred-card">
                        <div class="label">Model Confidence</div>
                        <div class="value" style="color:{r2_color}">{r2}%</div>
                        <div class="sub">R² score</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.pyplot(fig)

                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("📋 View Full Forecast Table"):
                    rows = [("Date", "Predicted Price", "Change from Today")]
                    rows += [
                        (
                            d.strftime("%b %d, %Y"),
                            f"{p:.2f}",
                            f"{'▲' if ((p-current)/current*100)>=0 else '▼'} "
                            f"{abs((p - current) / current * 100):.2f}%"
                            if current else "—"
                        )
                        for d, p in zip(future_dates, predictions)
                    ]
                    header = "| Date | Predicted Price | Change from Today |"
                    divider = "|------|----------------|-------------------|"
                    table_md = header + "\n" + divider + "\n"
                    for r in rows[1:]:
                        table_md += f"| {r[0]} | {r[1]} | {r[2]} |\n"
                    st.markdown(table_md)

                # ── R² note ────────────────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                if r2 >= 80:
                    st.success(f"✅ **R² = {r2}%** — Strong trend detected. Model fits the data well.")
                elif r2 >= 50:
                    st.warning(f"⚠️ **R² = {r2}%** — Moderate fit. Predictions show direction, not exact prices.")
                else:
                    st.error(f"❌ **R² = {r2}%** — Weak fit. Stock is volatile; use predictions with caution.")

                st.caption(
                    "⚠️ Disclaimer: Predictions use Linear Regression on past price data. "
                    "They are for educational purposes only — not financial advice. "
                    "Past trends do not guarantee future results."
                )

                st.session_state.logs.insert(0,
                    f"[{time.strftime('%H:%M:%S')}] Prediction: {pred_symbol} "
                    f"({hist_period}, {forecast_days}d) R²={r2}%")


# ─────────────────────────────────────────────────────────────
# TAB 3 — Email Setup
# ─────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 📧 Email Alert Configuration")
    st.markdown(
        "Fill in your Gmail details below. When the stock hits your target price, "
        "an alert email is sent automatically."
    )
    st.markdown("---")

    st.markdown("#### 🔑 Step 1 — Get a Gmail App Password")
    st.info(
        "You **cannot** use your regular Gmail password. "
        "Go to **myaccount.google.com → Security → 2-Step Verification → App Passwords**, "
        "generate one for Mail, and copy the 16-character code (e.g. `abcd efgh ijkl mnop`)."
    )

    st.markdown("#### ✉️ Step 2 — Enter Your Credentials")
    col_a, col_b = st.columns(2)
    with col_a:
        sender_input   = st.text_input("📤 Your Gmail (sender)",
                                        value=st.session_state.cfg_sender,
                                        placeholder="yourname@gmail.com")
        password_input = st.text_input("🔑 App Password",
                                        value=st.session_state.cfg_password,
                                        type="password",
                                        placeholder="abcd efgh ijkl mnop")
    with col_b:
        receiver_input = st.text_input("📥 Receiver Email",
                                        value=st.session_state.cfg_receiver,
                                        placeholder="receiver@gmail.com")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("💡 **Tip:** Use the same Gmail for sender and receiver to test on yourself.")

    st.markdown("<br>", unsafe_allow_html=True)
    cs, ct, cc = st.columns(3)

    with cs:
        if st.button("💾 Save Settings"):
            if sender_input and password_input and receiver_input:
                st.session_state.cfg_sender   = sender_input
                st.session_state.cfg_password = password_input
                st.session_state.cfg_receiver = receiver_input
                st.success("✅ Saved! Email will fire when the stock hits your target.")
            else:
                st.error("Please fill in all three fields.")

    with ct:
        if st.button("🧪 Send Test Email"):
            s = st.session_state.cfg_sender   or sender_input
            p = st.session_state.cfg_password or password_input
            r = st.session_state.cfg_receiver or receiver_input
            if s and p and r:
                with st.spinner("Sending..."):
                    ok, result = send_email(s, p, r, symbol or "TCS.NS", 4200.0, 4000.0)
                if ok:
                    st.success(f"✅ Test email sent to **{r}**! Check your inbox.")
                else:
                    st.error(f"❌ Failed: {result}")
                st.session_state.logs.insert(0,
                    f"[{time.strftime('%H:%M:%S')}] Test email → "
                    f"{'✅ OK' if ok else '❌ ' + result}")
            else:
                st.warning("Fill in and save all fields first.")

    with cc:
        if st.button("🗑️ Clear Settings"):
            st.session_state.cfg_sender   = ""
            st.session_state.cfg_password = ""
            st.session_state.cfg_receiver = ""
            st.success("Email settings cleared.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.cfg_sender:
        st.markdown(f"""
        <div style="background:#1a2e1a;border:1px solid #36d68a;border-radius:10px;
                    padding:14px 20px;color:#36d68a;font-size:14px;">
            ✅ <b>Email configured</b> — alerts will fire to
            <code>{st.session_state.cfg_receiver}</code>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#2a2310;border:1px solid #f7c948;border-radius:10px;
                    padding:14px 20px;color:#f7c948;font-size:14px;">
            ⚠️ <b>Not configured yet</b> — fill in the fields above and click Save Settings.
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>")
    with st.expander("❓ Common Errors & Fixes"):
        st.markdown("""
| Error | Cause | Fix |
|---|---|---|
| `SMTPAuthenticationError` | Wrong password or 2FA off | Enable 2-Step Verification first, then generate App Password |
| `Connection refused` | Port 465 blocked | Try from a different Wi-Fi / network |
| Email goes to Spam | First-time sender | Open Spam folder → click "Not Spam" |
| `Username/Password not accepted` | Using real Gmail password | Must use the 16-char App Password |
        """)


with tab4:
    st.markdown("### 🗒️ Activity Log")
    if st.session_state.logs:
        log_html = "<br>".join(st.session_state.logs[:30])
        st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="log-box">No activity yet. Fetch a stock to begin.</div>',
            unsafe_allow_html=True
        )
    st.markdown("<br>")
    if st.button("🗑️ Clear Log"):
        st.session_state.logs = []
        st.rerun()

st.markdown("---")
st.caption(
    "💡 Streamlit doesn't auto-refresh on its own — click Refresh Price Now in the sidebar. "
    "For automatic updates install streamlit-autorefresh and add "
    "st_autorefresh(interval=60000) near the top of the file."
)