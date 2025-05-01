import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import QuantLib as ql

def plot_payoff(S_grid, K, model_price, opt_type):
    """Payoff at expiration vs underlying S, with model price line."""
    df = pd.DataFrame({
        "S": S_grid,
        "Payoff": np.maximum((S_grid - K) if opt_type=="call" else (K - S_grid), 0)
    })
    fig = px.line(
        df, x="S", y="Payoff",
        title="Payoff at Expiration",
        labels={"S":"Underlying Price", "Payoff":"Payoff"},
        template="plotly_dark"
    )
    fig.add_hline(
        y=model_price,
        line_dash="dash",
        annotation_text="Model Price",
        annotation_position="bottom right",
    )
    return fig

def price_surface(S, Ks, Ts, r, sigma, opt_type, price_func):
    """3D surface of price vs. strike (Ks) and maturity (Ts)."""
    Z = [[ price_func(S, K_, r, sigma, T_, opt_type) for K_ in Ks ] for T_ in Ts]
    fig = go.Figure(data=[go.Surface(x=Ks, y=Ts, z=Z)])
    fig.update_layout(
      title="Option Price Surface",
      scene=dict(
        xaxis_title="Strike",
        yaxis_title="Time to Maturity (yrs)",
        zaxis_title="Price"
      ),
      template="plotly_dark"
    )
    return fig

def implied_vol_smile(S, Ks, r, T, opt_type, market_prices):
    """
    Implied volatility vs strike: solve for σ that matches market_prices
    using QuantLib's impliedVolatility method.
    """
    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today
    flat_ts = ql.YieldTermStructureHandle(
        ql.FlatForward(today, r, ql.Actual365Fixed())
    )
    vols = []
    for K_, mp in zip(Ks, market_prices):
        try:
            payoff = ql.PlainVanillaPayoff(
                ql.Option.Call if opt_type=="call" else ql.Option.Put, K_
            )
            exercise = ql.EuropeanExercise(today + int(T*365))
            opt = ql.VanillaOption(payoff, exercise)
            process = ql.BlackScholesMertonProcess(
                ql.QuoteHandle(ql.SimpleQuote(S)),
                flat_ts,
                flat_ts,
                ql.BlackVolTermStructureHandle(
                    ql.BlackConstantVol(today, ql.NullCalendar(), 0.2, ql.Actual365Fixed())
                )
            )
            opt.setPricingEngine(ql.AnalyticEuropeanEngine(process))
            iv = opt.impliedVolatility(
                mp, process, 1e-6, 100, 0.0, 5.0
            )
        except Exception:
            iv = np.nan
        vols.append(iv)
    df = pd.DataFrame({"Strike": Ks, "ImpliedVol": vols})
    fig = px.line(
        df, x="Strike", y="ImpliedVol",
        title="Implied Volatility Smile",
        labels={"ImpliedVol":"Implied Volatility"},
        template="plotly_dark"
    )
    return fig

def greek_surface(S_grid, K, T_grid, r, sigma, opt_type, greek_func, name):
    """3D surface of a single Greek vs S (or K) and T."""
    # here greek_func takes (S,K,r,sigma,T,opt_type)
    Z = [[ greek_func(S_, K, r, sigma, T_, opt_type) for S_ in S_grid ] for T_ in T_grid]
    fig = go.Figure(data=[go.Surface(x=S_grid, y=T_grid, z=Z)])
    fig.update_layout(
      title=f"{name} Surface",
      scene=dict(xaxis_title="Underlying Price", yaxis_title="Time to Maturity", zaxis_title=name),
      template="plotly_dark"
    )
    return fig

def animate_paths(df_paths, var_name):
    """Animate time-series DataFrame (index=time, columns=paths)."""
    df = df_paths.reset_index().melt(id_vars="index", var_name="Path", value_name=var_name)
    fig = px.line(
        df, x="index", y=var_name, color="Path",
        animation_frame="index",
        range_y=[df[var_name].min()*0.9, df[var_name].max()*1.1],
        title=f"{var_name} Paths Animation",
        labels={"index":"Time"},
        template="plotly_dark"
    )
    fig.update_layout(yaxis_title=var_name)
    return fig
