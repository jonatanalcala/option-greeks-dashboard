from setuptools import setup, find_packages

setup(
    name="option_greeks_dashboard",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scipy>=1.10.0",
        "sympy>=1.12.0",
        "QuantLib-Python",
        "plotly>=5.15.0",
        "streamlit>=1.25.0",
        "yfinance>=0.2.28",
        "pandas-datareader>=0.10.0",
        "polars>=0.18.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0"],
    },
    entry_points={
        "console_scripts": [
            "ogd=option_greeks_dashboard.ui.app:main"
        ]
    },
)
