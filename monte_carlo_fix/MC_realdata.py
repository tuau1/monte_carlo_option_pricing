import numpy as np
import yfinance as yf

np.random.seed(42)

ticker = "AAPL"
data = yf.download(ticker, period="1y")

prices = data["Close"].squeeze()
daily_returns = prices.pct_change().dropna()

S = float(prices.iloc[-1])
daily_sigma = float(daily_returns.std())
annual_sigma = daily_sigma * np.sqrt(252)

print("Latest price:", round(S, 2))
print("Daily volatility:", round(daily_sigma, 4))
print("Annual volatility:", round(annual_sigma, 4))

from scipy.stats import norm

K = 345
T = 76 / 365
r = 0.038   # replace with the current 3-month Treasury yield

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

stock = yf.Ticker(ticker)
print(stock.options)

expiry = "2027-01-15"   # replace with the date you picked
chain = stock.option_chain(expiry)
calls = chain.calls
print(calls[calls["strike"] == 345][["strike", "bid", "ask", "lastPrice", "impliedVolatility"]])


from scipy.optimize import brentq

def bs_call_price(sigma):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

market_price = (17.4 + 18.2) / 2

implied_vol = brentq(lambda sigma: bs_call_price(sigma) - market_price, 0.01, 2.0)

print("Market price:", market_price)
print("Implied volatility:", round(implied_vol, 4))
print("Historical volatility:", round(annual_sigma, 4))





