import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

S = 100
K = 110
r = 0.05
num_simulations = 100000
batch = 10000     # simulate in batches so long expirations don't run out of memory

def mc_call_put(annual_sigma, T):
    days = int(252 * T)
    daily_sigma = annual_sigma / np.sqrt(252)
    ending_prices = np.empty(num_simulations)
    for start in range(0, num_simulations, batch):
        returns = np.random.normal(r / 252, daily_sigma, size=(batch, days))
        ending_prices[start:start + batch] = S * np.prod(1 + returns, axis=1)
    discount = (1 + r) ** T
    call = np.mean(np.maximum(ending_prices - K, 0)) / discount
    put = np.mean(np.maximum(K - ending_prices, 0)) / discount
    return call, put

# ---------- Price vs volatility (1 year to expiration) ----------
vols = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
vol_calls, vol_puts = [], []
for v in vols:
    call, put = mc_call_put(v, 1)
    vol_calls.append(call)
    vol_puts.append(put)
    print("Volatility", v, "-> call:", round(call, 2), "put:", round(put, 2))

plt.figure()
plt.plot(vols, vol_calls, marker="o", label="Call")
plt.plot(vols, vol_puts, marker="o", label="Put")
plt.title("Option price vs volatility")
plt.xlabel("Annual volatility")
plt.ylabel("Option price ($)")
plt.legend()
plt.savefig("volatility.png")

# ---------- Price vs time (daily volatility 2%) ----------
annual_sigma = 0.02 * np.sqrt(252)
times = [0.1, 0.25, 0.5, 1, 2, 3]
time_calls, time_puts = [], []
for T in times:
    call, put = mc_call_put(annual_sigma, T)
    time_calls.append(call)
    time_puts.append(put)
    print("Years", T, "-> call:", round(call, 2), "put:", round(put, 2))

plt.figure()
plt.plot(times, time_calls, marker="o", label="Call")
plt.plot(times, time_puts, marker="o", label="Put")
plt.title("Option price vs time to expiration")
plt.xlabel("Years to expiration")
plt.ylabel("Option price ($)")
plt.legend()
plt.savefig("time.png")
plt.show()
