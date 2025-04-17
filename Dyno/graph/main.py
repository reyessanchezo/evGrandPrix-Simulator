from typing import Any

import matplotlib.pyplot as plt
import numpy as np

p = 1.0
c = 0.8
m = 136.0
g = 9.8
a = 0.5
r = 1.2
d = 0.254
gr = 9.0 / 68


def rpm_to_v(x) -> float:
    return (x / 60) * np.pi * d * gr


def w(x: Any) -> float:
    return (0.005 + (1 / p) * (0.01 + 0.0095 * pow((3.6 * x / 100), 2))) * m * g + (
        1 / 2
    ) * c * a * r * pow(x, 2)


x = np.arange(0, 5001, 100, np.int64)
y = w(rpm_to_v(x))

print(x)
print(y)

x2 = np.array([500, 2500, 4500])
y2 = w(rpm_to_v(x2))

print(x2)
print(y2)

labels = []

for i in range(x2.shape[0]):
    labels.append(f"RPM: {x2[i]}\nWatts: {y2[i]:.2f}")

plt.figure(figsize=(10, 8))
plt.plot(x, y, color="red")

plt.xlim(left=0)

ax = plt.gca()
plt.grid(axis="y", linestyle="-", alpha=0.7)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.ylabel("Watts", fontsize=16, fontweight="bold")
plt.xlabel("RPM", fontsize=16, fontweight="bold")

plt.scatter(x2, y2, color="black", zorder=3)

for i, label in enumerate(labels):
    plt.annotate(
        label,
        (x2[i], y2[i]),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
        fontsize=16,
        color="black",
        bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.7"),
    )

plt.tight_layout()
plt.savefig("Figure_1.png")
