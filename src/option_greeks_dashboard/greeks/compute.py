# src/option_greeks_dashboard/greeks/compute.py

import QuantLib as ql

def _make_european_option(S, K, r, sigma, T, option_type):
    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today
    maturity = today + int(T * 365)

    payoff = ql.PlainVanillaPayoff(
        ql.Option.Call if option_type == "call" else ql.Option.Put,
        K
    )
    exercise = ql.EuropeanExercise(maturity)

    spot_handle = ql.QuoteHandle(ql.SimpleQuote(S))
    flat_ts = ql.YieldTermStructureHandle(
        ql.FlatForward(today, r, ql.Actual365Fixed())
    )
    vol_ts = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(today, ql.NullCalendar(), sigma, ql.Actual365Fixed())
    )

    bsm_process = ql.BlackScholesMertonProcess(
        spot_handle,
        flat_ts,
        flat_ts,
        vol_ts
    )

    option = ql.VanillaOption(payoff, exercise)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
    return option

def black_scholes_price(S, K, r, sigma, T, option_type="call"):
    opt = _make_european_option(S, K, r, sigma, T, option_type)
    return opt.NPV()

def delta(S, K, r, sigma, T, option_type="call"):
    opt = _make_european_option(S, K, r, sigma, T, option_type)
    return opt.delta()

def gamma(S, K, r, sigma, T, option_type="call"):
    opt = _make_european_option(S, K, r, sigma, T, option_type)
    return opt.gamma()

def theta(S, K, r, sigma, T, option_type="call"):
    # QL returns theta per year, divide by 365 for per-day decay if you prefer
    opt = _make_european_option(S, K, r, sigma, T, option_type)
    return opt.theta() / 365.0

def vega(S, K, r, sigma, T, option_type="call"):
    opt = _make_european_option(S, K, r, sigma, T, option_type)
    return opt.vega()

def rho(S, K, r, sigma, T, option_type="call"):
    opt = _make_european_option(S, K, r, sigma, T, option_type)
    return opt.rho()
