import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from option_greeks_dashboard.pricing.black_scholes import (
    black_scholes_price,
    black_scholes_price_binomial,
)
from option_greeks_dashboard.greeks.compute import delta, gamma, theta, vega, rho
from option_greeks_dashboard.data.loader import fetch_historical_prices
from option_greeks_dashboard.utils.helpers import simulate_gbm, simulate_ou, simulate_vg
from option_greeks_dashboard.utils.plotting import (
    plot_payoff, price_surface, implied_vol_smile,
    greek_surface, animate_paths
)

# ─── Page Config & Title ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Option Pricing & Risk Explorer",
    page_icon="📈",
    layout="wide",
)
st.title("Option Pricing & Risk Explorer")

# ─── Sidebar About & Inputs ────────────────────────────────────────────────────
with st.sidebar.expander("🔍 About & Learning Objectives"):
    st.markdown("""
    - Understand how **price** and **Greeks** respond to changes in S, K, σ, T, r  
    - Visualize the **volatility smile** via strike/maturity surfaces  
    - Compute and plot **implied volatility** smiles  
    - Explore **3D Greek surfaces** (Δ, Θ, Γ) over (S,T)  
    - Compare **analytic** vs **binomial** pricing engines  
    - Animate **stochastic paths** to internalize model dynamics  
    """)
    st.caption("Tip: σ is annualized volatility (e.g. 20% = 0.20).")

with st.sidebar:
    st.header("Input Parameters")
    
    S = st.number_input(
        "Underlying Price (S)",
        min_value=0.01, max_value=1000.0, value=100.0, step=1.0,
        help="The current spot price of the underlying asset, e.g. stock price."
    )
    st.caption("Spot price of the underlying security.")
    
    K = st.number_input(
        "Strike Price (K)",
        min_value=0.01, max_value=1000.0, value=100.0, step=1.0,
        help="The strike or exercise price at which the option can be exercised."
    )
    st.caption("Strike price defining the payoff boundary.")
    
    T = st.slider(
        "Time to Maturity (Years)",
        min_value=0.01, max_value=5.0, value=1.0, step=0.01,
        help="Time until expiration, expressed in years (e.g. 0.5 = 6 months)."
    )
    st.caption("Time remaining until option expiration.")
    
    r = st.slider(
        "Risk-free Rate (r)",
        min_value=0.0, max_value=0.2, value=0.01, step=0.001,
        help="Continuously compounded annual risk-free interest rate (decimal)."
    )
    st.caption("Annual risk-free rate (e.g. 0.01 = 1%).")
    
    sigma = st.slider(
        "Volatility (σ)",
        min_value=0.01, max_value=1.0, value=0.2, step=0.01,
        help="Annualized volatility of the underlying (standard deviation, decimal)."
    )
    st.caption("Annualized volatility (e.g. 0.2 = 20%).")
    
    opt_type = st.selectbox(
        "Option Type", ["call", "put"],
        help="Select ‘call’ for the right to buy, ‘put’ for the right to sell."
    )
    
    engine = st.selectbox(
        "Pricing Engine", ["Analytic", "Binomial"],
        help="Choose analytic Black-Scholes or a discrete binomial tree model."
    )
    if engine == "Binomial":
        steps = st.number_input(
            "Binomial Steps",
            min_value=10, max_value=2000, value=100, step=10,
            help="Number of time steps in the binomial tree."
        )
        tree = st.selectbox(
            "Binomial Tree", ["crr", "jr", "td", "tr", "lr"],
            help="Tree construction method: Cox–Ross–Rubinstein (crr), Jarrow–Rudd (jr), etc."
        )
    
    st.markdown("---")
    
    ticker = st.text_input(
        "Historical Ticker", "AAPL",
        help="Ticker symbol for fetching historical price data."
    )
    period = st.selectbox(
        "History Period", ["1y","6mo","3mo","1mo"],
        help="Time window for historical data plotting."
    )


# ─── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "Metrics", "Sensitivity", "Surface & Smile", "Greek Surfaces",
    "Payoff", "Historical", "Processes"
])

# ─── 1. Metrics ─────────────────────────────────────────────────────────────────
with tabs[0]:
    st.subheader("Option Metrics")
    if T <= 0 or sigma <= 0:
        st.error("Maturity and volatility must be positive.")
    else:
        # Choose pricing engine so each function gets the right args
        if engine == "Analytic":
            price = black_scholes_price(
                S, K, r, sigma, T, opt_type
            )
        else:
            price = black_scholes_price_binomial(
                S, K, r, sigma, T, opt_type,
                steps,  # required for binomial
                tree    # required for binomial
            )

        # Compute Greeks
        d  = delta(S, K, r, sigma, T, opt_type)
        g  = gamma(S, K, r, sigma, T)
        th = theta(S, K, r, sigma, T, opt_type)
        v  = vega(S, K, r, sigma, T)
        rh = rho(S, K, r, sigma, T, opt_type)

        # Display metrics
        cols = st.columns(3)
        cols[0].metric("Price", f"{price:.4f}")
        cols[1].metric("Delta", f"{d:.4f}")
        cols[2].metric("Gamma", f"{g:.4f}")
        cols = st.columns(3)
        cols[0].metric("Theta", f"{th:.4f}")
        cols[1].metric("Vega", f"{v:.4f}")
        cols[2].metric("Rho", f"{rh:.4f}")

        # 1) Greek definitions
        with st.expander("🔍 What each Greek means"):
            st.markdown("""
            - **Delta (Δ):** Sensitivity of option price to a small change in underlying price.  
            - **Gamma (Γ):** Rate of change of Delta with respect to underlying price.  
            - **Theta (Θ):** Time decay of option price (per day).  
            - **Vega (ν):** Sensitivity of option price to volatility.  
            - **Rho (ρ):** Sensitivity of option price to interest rate.  
            """)

        # 2) Bar chart of current Greeks
        greek_df = pd.DataFrame({
            "Greek": ["Delta","Gamma","Theta","Vega","Rho"],
            "Value": [d, g, th, v, rh]
        })
        st.subheader("Greeks Overview")
        st.caption("Bar chart of current Greek values for your inputs.")
        fig_bar = px.bar(
            greek_df, x="Greek", y="Value",
            title="Current Greeks", template="plotly_dark"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ─── 2. Sensitivity ──────────────────────────────────────────────────────────────
with tabs[1]:
    st.subheader("Greeks vs Volatility")
    sigs = np.linspace(0.01, 1.0, 50)
    data = {
        "σ": sigs,
        "Delta": [delta(S, K, r, s, T, opt_type) for s in sigs],
        "Gamma": [gamma(S, K, r, s, T) for s in sigs],
        "Theta": [theta(S, K, r, s, T, opt_type) for s in sigs],
        "Vega": [vega(S, K, r, s, T) for s in sigs],
        "Rho": [rho(S, K, r, s, T, opt_type) for s in sigs],
    }
    df = pd.DataFrame(data).melt(id_vars="σ", var_name="Greek", value_name="Value")
    st.caption("Shows how each Greek changes as volatility varies.")
    fig = px.line(df, x="σ", y="Value", color="Greek", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ─── 3. Surface & Smile ─────────────────────────────────────────────────────────
with tabs[2]:
    Ks = np.linspace(0.8*S, 1.2*S, 40)
    Ts = np.linspace(0.1, 2.0, 40)
    st.subheader("Price Surface")
    st.caption("3D surface of option price vs strike and maturity.")
    st.plotly_chart(
        price_surface(
            S, Ks, Ts, r, sigma, opt_type,
            black_scholes_price if engine=="Analytic"
            else lambda *args,**kw: black_scholes_price_binomial(*args, **kw)
        ),
        use_container_width=True
    )

    st.subheader("Implied Volatility Smile")
    st.caption("Solve σ to match model to (dummy) market prices.")
    mkt = [black_scholes_price(S, K_, r, sigma, T, opt_type) for K_ in Ks]
    st.plotly_chart(implied_vol_smile(S, Ks, r, T, opt_type, mkt), use_container_width=True)

# ─── 4. Greek Surfaces ──────────────────────────────────────────────────────────
with tabs[3]:
    Sg = np.linspace(0.5*S, 1.5*S, 30)
    Tg = np.linspace(0.1, 2.0, 30)
    for func,name in [(delta,"Delta"), (gamma,"Gamma"), (theta,"Theta")]:
        st.subheader(f"{name} Surface")
        st.caption(f"3D surface of {name} vs S and maturity.")
        st.plotly_chart(greek_surface(Sg, K, Tg, r, sigma, opt_type, func, name), use_container_width=True)

# ─── 5. Payoff Diagram ──────────────────────────────────────────────────────────
with tabs[4]:
    Sgrid = np.linspace(0.5*K, 1.5*K, 100)
    st.subheader("Payoff Diagram")
    st.caption("Payoff at expiration vs underlying price, with model price line.")
    st.plotly_chart(plot_payoff(Sgrid, K, price, opt_type), use_container_width=True)

# ─── 6. Historical Prices ───────────────────────────────────────────────────────
with tabs[5]:
    st.subheader(f"Historical Price: {ticker.upper()}")
    try:
        df = fetch_historical_prices(ticker, period)
        st.caption("Daily close prices over the chosen period.")
        fig = px.line(df, x="Date", y="Close", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching {ticker}: {e}")

# ─── 7. Processes (Static) with Descriptive Legend ────────────────────────────
with tabs[6]:
    st.subheader("Simulated Stochastic Processes")
    Tproc, steps_proc, n_paths = 1.0, 200, 5

    # GBM (static)
    gbm_df = simulate_gbm(S, r, sigma, Tproc, steps_proc, n_paths, seed=42)
    st.markdown("**Geometric Brownian Motion**")
    fig_gbm = px.line(
        gbm_df,
        labels={"index": "Time", "value": "S(t)"},
        title="GBM Paths (Static)",
        template="plotly_dark"
    )
    fig_gbm.update_layout(legend_title_text="Simulation Path")
    st.plotly_chart(fig_gbm, use_container_width=True)

    # OU (static)
    ou_df = simulate_ou(0.0, 1.0, 0.0, 0.3, Tproc, steps_proc, n_paths, seed=42)
    st.markdown("**Ornstein–Uhlenbeck Process**")
    fig_ou = px.line(
        ou_df,
        labels={"index": "Time", "value": "X(t)"},
        title="OU Paths (Static)",
        template="plotly_dark"
    )
    fig_ou.update_layout(legend_title_text="Simulation Path")
    st.plotly_chart(fig_ou, use_container_width=True)

    # VG (static)
    vg_df = simulate_vg(S, 0.1, sigma, 0.2, Tproc, steps_proc, n_paths, seed=42)
    st.markdown("**Variance Gamma Process**")
    fig_vg = px.line(
        vg_df,
        labels={"index": "Time", "value": "S(t)"},
        title="VG Paths (Static)",
        template="plotly_dark"
    )
    fig_vg.update_layout(legend_title_text="Simulation Path")
    st.plotly_chart(fig_vg, use_container_width=True)