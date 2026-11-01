import numpy as np
import yfinance as yf
from scipy.stats import norm
from scipy.optimize import brentq

np.random.seed(42)

ticker = "AAPL"
# fixed one-year window (the last close is 2026-10-30) so the results can be reproduced
data = yf.download(ticker, start="2025-10-31", end="2026-10-31", auto_adjust=False)

prices = data["Close"].squeeze()
daily_returns = prices.pct_change().dropna()

S = float(prices.iloc[-1])
daily_sigma = float(daily_returns.std())
annual_sigma = daily_sigma * np.sqrt(252)

print("Latest price:", round(S, 2))
print("Daily volatility:", round(daily_sigma, 4))
print("Annual volatility:", round(annual_sigma, 4))

K = 345
T = 76 / 365   # 76 days counted from 2026-10-31 (the day after the last close) to the 2027-01-15 expiration
r = 0.0397     # 3-month Treasury bill rate at the 2026-10-30 close (Yahoo ^IRX)

d1 = (np.log(S / K) + (r + annual_sigma**2 / 2) * T) / (annual_sigma * np.sqrt(T))
d2 = d1 - annual_sigma * np.sqrt(T)
bs_call = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

steps = int(252 * T)   # trading days until expiration
dt = T / steps         # length of each step, so the simulation covers exactly T years
returns = np.random.normal(r * dt, annual_sigma * np.sqrt(dt), size=(100000, steps))
ending_prices = S * np.prod(1 + returns, axis=1)
mc_call = np.mean(np.maximum(ending_prices - K, 0)) / (1 + r) ** T

print("Black-Scholes call:", round(bs_call, 2))
print("Monte Carlo call:", round(mc_call, 2))

expiry = "2027-01-15"
try:
    calls = yf.Ticker(ticker).option_chain(expiry).calls
    print("Live quote (for reference; the calculation below uses the saved 2026-10-30 bid/ask):")
    print(calls[calls["strike"] == K][["strike", "bid", "ask", "lastPrice"]])
except ValueError:
    print("The", expiry, "option is no longer listed, so using the saved bid/ask below.")

def bs_call_price(sigma):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

market_price = (17.4 + 18.2) / 2   # bid/ask midpoint at the 2026-10-30 close

implied_vol = brentq(lambda sigma: bs_call_price(sigma) - market_price, 0.01, 2.0)

print("Market price:", round(market_price, 2))
print("Implied volatility:", round(implied_vol, 4))
print("Historical volatility:", round(annual_sigma, 4))
