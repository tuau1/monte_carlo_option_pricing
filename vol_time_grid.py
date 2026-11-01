import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# ---------- Inputs ----------
S = 100          # neutral starting price, so the comparison is easy to read
r = 0.038
n_show = 60      # paths drawn per panel
n_dist = 10000   # paths used for the spread and the distributions

# ---------- Colors ----------
c_avg = "#1d3557"
c_start = "#8d99ae"
c_dist = ["#a8dadc", "#457b9d", "#1d3557"]

def simulate(sigma, T, n):
    days = int(252 * T)
    daily_sigma = sigma / np.sqrt(252)
    rets = np.random.normal(r / 252, daily_sigma, size=(n, days))
    p = S * np.cumprod(1 + rets, axis=1)
    return np.hstack([np.full((n, 1), S), p]), days

fig, axes = plt.subplots(3, 3, figsize=(15, 12))

def style(ax):
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.grid(alpha=0.25)

# ---------- Row 1: volatility changes, time fixed ----------
vols = [0.08, 0.16, 0.32]
vol_endings = []
for ax, sigma in zip(axes[0], vols):
    paths, days = simulate(sigma, 1, n_dist)
    x = np.linspace(0, 1, days + 1)
    for p in paths[:n_show]:
        ax.plot(x, p, linewidth=0.7, alpha=0.6)
    ax.plot(x, paths.mean(axis=0), color=c_avg, linewidth=2)
    ax.axhline(S, color=c_start, linestyle="--", linewidth=1)
    spread = paths[:, -1].std()
    vol_endings.append(paths[:, -1])
    ax.set_title(f"σ = {sigma:.0%}, T = 1 year   (spread = {spread:.1f})", fontsize=11)
    ax.set_ylim(40, 180)
    ax.set_xlabel("Years")
    style(ax)
axes[0][0].set_ylabel("Price ($)")

# ---------- Row 2: time changes, volatility fixed ----------
times = [0.25, 1, 4]
time_endings = []
for ax, T in zip(axes[1], times):
    paths, days = simulate(0.16, T, n_dist)
    x = np.linspace(0, T, days + 1)
    for p in paths[:n_show]:
        ax.plot(x, p, linewidth=0.7, alpha=0.6)
    ax.plot(x, paths.mean(axis=0), color=c_avg, linewidth=2)
    ax.axhline(S, color=c_start, linestyle="--", linewidth=1)
    spread = paths[:, -1].std()
    time_endings.append(paths[:, -1])
    ax.set_title(f"σ = 16%, T = {T} years   (spread = {spread:.1f})", fontsize=11)
    ax.set_ylim(30, 260)
    ax.set_xlabel("Years")
    style(ax)
axes[1][0].set_ylabel("Price ($)")

# ---------- Row 3: ending-price distributions ----------
ax = axes[2][0]
for endings, sigma, c in zip(vol_endings, vols, c_dist):
    ax.hist(endings, bins=80, range=(0, 320), density=True, alpha=0.6, color=c, label=f"σ = {sigma:.0%}")
ax.set_title("Ending prices, T = 1 year", fontsize=11)
ax.set_xlabel("Price ($)")
ax.legend()
style(ax)

ax = axes[2][1]
for endings, T, c in zip(time_endings, times, c_dist):
    ax.hist(endings, bins=80, range=(0, 320), density=True, alpha=0.6, color=c, label=f"T = {T} years")
ax.set_title("Ending prices, σ = 16%", fontsize=11)
ax.set_xlabel("Price ($)")
ax.legend()
style(ax)

ax = axes[2][2]
ax.axis("off")
ax.text(0.02, 0.85, "What this shows", fontsize=13, fontweight="bold", color=c_avg)
ax.text(0.02, 0.15,
        "The spread of outcomes grows with σ × √T.\n\n"
        "• Double the volatility → double the spread\n"
        "• 16× the time → only 4× the spread (√16 = 4)\n"
        "• Distributions skew right: prices can't\n"
        "  fall below $0, but have no upper limit\n\n"
        "A wider spread raises both call and put\n"
        "values, because an option's downside\n"
        "is capped at $0.",
        fontsize=10.5, color="#333333", va="bottom")

fig.suptitle("How volatility and time shape Monte Carlo outcomes",
             fontsize=16, fontweight="bold", x=0.04, ha="left")
fig.text(0.04, 0.005,
         "Row 1: volatility varies, time fixed. Row 2: time varies, volatility fixed. "
         f"{n_dist:,} simulations per panel ({n_show} shown).",
         fontsize=8.5, color="gray")

plt.tight_layout(rect=[0, 0.02, 1, 0.96])
plt.savefig("vol_time_grid.png", dpi=200, bbox_inches="tight")
plt.show()
