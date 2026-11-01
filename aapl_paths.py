import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.stats import norm

np.random.seed(42)

# ---------- Inputs ----------
ticker = "AAPL"
K = 345
T = 76 / 365
r = 0.038         # 3-month Treasury yield
expiry = "2027-01-15"

# ---------- Data ----------
data = yf.download(ticker, period="1y", progress=False)
prices = data["Close"].squeeze()
daily_returns = prices.pct_change().dropna()

S = float(prices.iloc[-1])
daily_sigma = float(daily_returns.std())
annual_sigma = daily_sigma * np.sqrt(252)
days = int(252 * T)

# ---------- Pricing (100,000 simulations) ----------
all_returns = np.random.normal(r / 252, daily_sigma, size=(100000, days))
ending_all = S * np.prod(1 + all_returns, axis=1)
mc_call = np.mean(np.maximum(ending_all - K, 0)) / (1 + r) ** T
prob_above = np.mean(ending_all > K)

d1 = (np.log(S / K) + (r + annual_sigma**2 / 2) * T) / (annual_sigma * np.sqrt(T))
d2 = d1 - annual_sigma * np.sqrt(T)
bs_call = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

# ---------- Paths for the chart ----------
def build_paths(n):
    p = S * np.cumprod(1 + all_returns[:n], axis=1)
    return np.hstack([np.full((n, 1), S), p])

paths = build_paths(200)       # lines shown on the chart
band = build_paths(5000)       # used for the average and the 90% range
x = np.arange(days + 1)
above = paths[:, -1] > K

# ---------- Colors ----------
c_above = "#2a9d8f"
c_below = "#b8bfc9"
c_strike = "#e63946"
c_avg = "#1d3557"
c_band = "#457b9d"

# ---------- Chart ----------
fig, (ax, axh) = plt.subplots(
    1, 2, figsize=(13, 6.5), sharey=True,
    gridspec_kw={"width_ratios": [4, 1], "wspace": 0.03}
)

for p, is_above in zip(paths, above):
    ax.plot(x, p, color=c_above if is_above else c_below, linewidth=0.8, alpha=0.45)

low = np.percentile(band, 5, axis=0)
high = np.percentile(band, 95, axis=0)
ax.fill_between(x, low, high, color=c_band, alpha=0.12, label="90% of outcomes")
ax.plot(x, band.mean(axis=0), color=c_avg, linewidth=2.5, label="Average path")

ax.axhline(K, color=c_strike, linestyle="-", linewidth=1.8, label=f"Strike ${K}")
ax.text(days, K, f"  Strike ${K}", color=c_strike, va="center", fontsize=9, fontweight="bold")

stats = (
    f"Spot ${S:.2f}  |  Strike ${K}\n"
    f"Volatility (hist.) {annual_sigma:.1%}  |  {days} trading days\n"
    f"Monte Carlo price ${mc_call:.2f}  |  Black-Scholes ${bs_call:.2f}\n"
    f"Chance of finishing above strike: {prob_above:.0%}"
)
ax.text(0.02, 0.97, stats, transform=ax.transAxes, va="top", fontsize=9.5,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor="#d0d4da"))

ax.set_xlabel("Trading days to expiration")
ax.set_ylabel("Price ($)")
ax.legend(loc="lower left", frameon=True, fontsize=9)
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
ax.grid(alpha=0.25)

axh.hist(ending_all[ending_all > K], bins=60, orientation="horizontal",
         color=c_above, alpha=0.7)
axh.hist(ending_all[ending_all <= K], bins=60, orientation="horizontal",
         color=c_below, alpha=0.9)
axh.axhline(K, color=c_strike, linestyle="-", linewidth=1.8)
axh.set_xlabel("Ending prices")
axh.set_xticks([])
for side in ["top", "right", "bottom"]:
    axh.spines[side].set_visible(False)

ax.set_ylim(np.percentile(ending_all, 0.5) * 0.95, np.percentile(ending_all, 99.5) * 1.03)

fig.suptitle(f"{ticker} call option: Monte Carlo simulation vs Black-Scholes",
             fontsize=15, fontweight="bold", x=0.06, ha="left")
fig.text(0.06, 0.01,
         "Model: 100,000 Monte Carlo simulations (200 shown) under risk-neutral pricing. "
         "Data: Yahoo Finance.",
         fontsize=8, color="gray")

plt.savefig("aapl_paths.png", dpi=220, bbox_inches="tight")
plt.show()
