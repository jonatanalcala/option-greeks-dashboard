import QuantLib as ql

from option_greeks_dashboard.greeks.compute import _make_european_option


def black_scholes_price(
    S: float,
    K: float,
    r: float,
    sigma: float,
    T: float,
    option_type: str = "call",
) -> float:
    """
    Analytic Black-Scholes price via QuantLib's AnalyticEuropeanEngine.
    """
    option = _make_european_option(S, K, r, sigma, T, option_type)
    return option.NPV()


def black_scholes_price_binomial(
    S: float,
    K: float,
    r: float,
    sigma: float,
    T: float,
    option_type: str = "call",
    steps: int = 100,
    tree: str = "crr",
) -> float:
    """
    Binomial‐tree Black-Scholes price via QuantLib.

    Parameters
    ----------
    steps
      Number of time steps in the tree.
    tree
      Tree type: "crr" (Cox–Ross–Rubinstein), "jr" (Jarrow–Rudd), etc.
    """
    # 1) Build the vanilla option (no engine yet)
    option = _make_european_option(S, K, r, sigma, T, option_type)

    # 2) Reconstruct the BSM process
    today = ql.Settings.instance().evaluationDate
    spot_handle = ql.QuoteHandle(ql.SimpleQuote(S))
    flat_ts = ql.YieldTermStructureHandle(
        ql.FlatForward(today, r, ql.Actual365Fixed())
    )
    vol_ts = ql.BlackVolTermStructureHandle(
        ql.FlatVol(today, ql.NullCalendar(), sigma, ql.Actual365Fixed())
    )
    bsm_process = ql.BlackScholesMertonProcess(
        spot_handle, flat_ts, flat_ts, vol_ts
    )

    # 3) Choose tree type
    engine_map = {
        "crr": ql.CoxRossRubinstein,
        "jr": ql.JarrowRudd,
        "td": ql.Tian,
        "tr": ql.Trigeorgis,
        "lr": ql.LeisenReimer,
    }
    tree_class = engine_map.get(tree.lower(), ql.CoxRossRubinstein)

    # 4) Attach binomial engine
    binomial_engine = ql.BinomialVanillaEngine(bsm_process, tree_class, steps)
    option.setPricingEngine(binomial_engine)

    return option.NPV()
