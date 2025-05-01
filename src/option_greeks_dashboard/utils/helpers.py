import numpy as np
import pandas as pd

def simulate_gbm(S0, mu, sigma, T, steps, n_paths=5, seed=None):
    """Simulate Geometric Brownian Motion paths."""
    if seed is not None:
        np.random.seed(seed)
    dt = T / steps
    t = np.linspace(0, T, steps + 1)
    paths = np.zeros((steps + 1, n_paths))
    paths[0] = S0
    for i in range(1, steps + 1):
        z = np.random.standard_normal(n_paths)
        paths[i] = paths[i-1] * np.exp((mu - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*z)
    return pd.DataFrame(paths, index=t, columns=[f"Path {i+1}" for i in range(n_paths)])

def simulate_ou(X0, kappa, theta, sigma, T, steps, n_paths=5, seed=None):
    """Simulate Ornstein–Uhlenbeck process paths."""
    if seed is not None:
        np.random.seed(seed)
    dt = T / steps
    t = np.linspace(0, T, steps + 1)
    paths = np.zeros((steps + 1, n_paths))
    paths[0] = X0
    for i in range(1, steps + 1):
        z = np.random.standard_normal(n_paths)
        paths[i] = paths[i-1] + kappa*(theta - paths[i-1])*dt + sigma*np.sqrt(dt)*z
    return pd.DataFrame(paths, index=t, columns=[f"Path {i+1}" for i in range(n_paths)])

def simulate_vg(S0, theta, sigma, nu, T, steps, n_paths=5, seed=None):
    """Simulate Variance Gamma process paths."""
    if seed is not None:
        np.random.seed(seed)
    dt = T / steps
    t = np.linspace(0, T, steps + 1)
    paths = np.zeros((steps + 1, n_paths))
    paths[0] = S0
    for i in range(1, steps + 1):
        gamma_inc = np.random.gamma(dt/nu, nu, n_paths)
        z = np.random.standard_normal(n_paths)
        paths[i] = paths[i-1] * np.exp(theta*gamma_inc + sigma*np.sqrt(gamma_inc)*z)
    return pd.DataFrame(paths, index=t, columns=[f"Path {i+1}" for i in range(n_paths)])

