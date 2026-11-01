import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

S = 100
K = 110
r = 0.05
daily_sigma = 0.02
T = 1
days = 252 * T

def mc_price(num_simulations):
    returns = np.random.normal(r / 252, daily_sigma, size=(num_simulations, days))
    ending_prices = S * np.prod(1 + returns, axis=1)
    payoffs = np.maximum(ending_prices - K, 0)
    return np.mean(payoffs) / (1 + r) ** T

def mc_put_price(num_simulations):
    returns = np.random.normal(r / 252, daily_sigma, size=(num_simulations, days))
    ending_prices = S * np.prod(1 + returns, axis=1)
    payoffs = np.maximum(K - ending_prices, 0)
    return np.mean(payoffs) / (1 + r) ** T

for n in [100, 1000, 10000, 100000]:
    print(n, "simulations:", round(mc_price(n), 2))

print("Black-Scholes: 10.72")

print("Put price (100,000 sims):", round(mc_put_price(100000), 2))

sim_counts = [100, 300, 1000, 3000, 10000, 30000, 100000]
prices = []

for n in sim_counts:
    prices.append(mc_price(n))

plt.plot(sim_counts, prices, marker="o", label="Monte Carlo")
plt.axhline(10.72, color="red", linestyle="--", label="Black-Scholes ($10.72)")
plt.xscale("log")
plt.title("Monte Carlo converges to Black-Scholes")
plt.xlabel("Number of simulations")
plt.ylabel("Call price ($)")
plt.legend()
plt.savefig("convergence.png")
plt.show()
