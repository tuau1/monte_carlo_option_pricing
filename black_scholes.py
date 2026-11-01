import numpy as np
from scipy.stats import norm

S = 100
K = 110
r = 0.05
sigma = 0.02 * np.sqrt(252)
T = 1

d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
d2 = d1 - sigma * np.sqrt(T)

call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

print("d1:", round(d1, 4))
print("d2:", round(d2, 4))
print("Call price:", round(call_price, 2))

put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
print("Put price:", round(put_price, 2))
