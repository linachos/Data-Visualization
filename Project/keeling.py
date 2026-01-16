import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Read CO2 data
co2_data = pd.read_csv("data/co2_mm_mlo.csv", comment="#")
co2_data["co2_ppm"] = co2_data["average"].replace(-99.99, np.nan)

# Calculate annual averages for cleaner visualization
annual_co2 = co2_data.groupby("year")["co2_ppm"].mean().reset_index()
annual_co2 = annual_co2[annual_co2["co2_ppm"] > 0]  # Remove missing values

# Get statistics
current_co2 = annual_co2["co2_ppm"].iloc[-1]
co2_1958 = annual_co2["co2_ppm"].iloc[0]
increase = current_co2 - co2_1958
percent_increase = (increase / co2_1958) * 100
year_400 = (
    annual_co2[annual_co2["co2_ppm"] >= 400]["year"].iloc[0]
    if len(annual_co2[annual_co2["co2_ppm"] >= 400]) > 0
    else 2013
)

# Create projection to 2050
last_year = annual_co2["year"].iloc[-1]
projection_years = np.arange(last_year + 1, 2051)
recent_rate = 2.5  # ppm per year (approximate current trend)
projection_values = current_co2 + (projection_years - last_year) * recent_rate

# Create figure with dark background
plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(16, 10))
fig.patch.set_facecolor("#1a1a2e")
ax.set_facecolor("#16213e")

# Plot the filled area (gradient effect using multiple fills)
x = annual_co2["year"]
y = annual_co2["co2_ppm"]

# Create gradient-like effect with multiple alpha values
for i in range(10):
    alpha = 0.1 + (i * 0.07)
    ax.fill_between(x, 280, y, alpha=alpha, color="#ff6b6b", linewidth=0)

# Plot main line
ax.plot(x, y, color="#ff6b6b", linewidth=3, label="Historical CO₂", zorder=5)

# Plot projection
projection_x = np.concatenate([[last_year], projection_years])
projection_y = np.concatenate([[current_co2], projection_values])
ax.plot(
    projection_x,
    projection_y,
    color="#ff6b6b",
    linewidth=3,
    linestyle="--",
    alpha=0.6,
    label="Projection to 2050",
    zorder=5,
)

# Add threshold lines
ax.axhline(
    y=350,
    color="#6bcf7f",
    linestyle="--",
    linewidth=2.5,
    label="Safe Level (350 ppm)",
    alpha=0.8,
    zorder=3,
)
ax.axhline(
    y=400,
    color="#ffd93d",
    linestyle="--",
    linewidth=2.5,
    label=f"400 ppm Milestone ({year_400})",
    alpha=0.8,
    zorder=3,
)
ax.axhline(
    y=415,
    color="#ff8e53",
    linestyle="--",
    linewidth=2.5,
    label="Pre-pandemic (415 ppm, 2019)",
    alpha=0.8,
    zorder=3,
)

# Add annotations for key points
ax.annotate(
    f"Current: {current_co2:.1f} ppm",
    xy=(last_year, current_co2),
    xytext=(last_year - 15, current_co2 + 25),
    fontsize=14,
    fontweight="bold",
    color="#ff6b6b",
    bbox=dict(
        boxstyle="round,pad=0.8", facecolor="#1a1a2e", edgecolor="#ff6b6b", linewidth=2
    ),
    arrowprops=dict(arrowstyle="->", color="#ff6b6b", lw=2),
)

ax.annotate(
    f"Projected 2050:\n{projection_values[-1]:.1f} ppm",
    xy=(2050, projection_values[-1]),
    xytext=(2035, projection_values[-1] + 20),
    fontsize=12,
    fontweight="bold",
    color="#ff6b6b",
    alpha=0.8,
    bbox=dict(
        boxstyle="round,pad=0.6",
        facecolor="#1a1a2e",
        edgecolor="#ff6b6b",
        linewidth=1.5,
        alpha=0.6,
    ),
    arrowprops=dict(arrowstyle="->", color="#ff6b6b", lw=1.5, alpha=0.6),
)

# Formatting
ax.set_xlabel("Year", fontsize=16, fontweight="bold", color="white")
ax.set_ylabel("CO₂ Concentration (ppm)", fontsize=16, fontweight="bold", color="white")
ax.set_title(
    "The Keeling Curve: CO₂ Levels Accelerating\nAtmospheric CO₂ Concentration (parts per million)",
    fontsize=22,
    fontweight="bold",
    color="white",
    pad=20,
)

# Add warning text
fig.text(
    0.5,
    0.92,
    "⚠️ Each part per million makes Earth hotter ⚠️",
    ha="center",
    fontsize=16,
    style="italic",
    color="#ff6b6b",
    fontweight="bold",
)

# Grid
ax.grid(True, alpha=0.2, linestyle="-", linewidth=0.5, color="white")
ax.set_axisbelow(True)

# Legend
legend = ax.legend(
    loc="upper left",
    fontsize=12,
    framealpha=0.9,
    facecolor="#1a1a2e",
    edgecolor="white",
)
for text in legend.get_texts():
    text.set_color("white")

# Tick styling
ax.tick_params(colors="white", labelsize=12)
for spine in ax.spines.values():
    spine.set_color("white")
    spine.set_linewidth(1.5)

# Set x-axis limits
ax.set_xlim(1955, 2053)
ax.set_ylim(300, max(projection_values[-1] + 20, 520))

# Add statistics box
stats_text = f"""KEY STATISTICS
━━━━━━━━━━━━━━━━━━
1958 Baseline: {co2_1958:.1f} ppm
Current (2024): {current_co2:.1f} ppm
Total Increase: +{increase:.1f} ppm
Percent Change: +{percent_increase:.1f}%
400 ppm Crossed: {year_400}
Projected 2050: {projection_values[-1]:.1f} ppm"""

ax.text(
    0.02,
    0.98,
    stats_text,
    transform=ax.transAxes,
    fontsize=11,
    verticalalignment="top",
    fontfamily="monospace",
    bbox=dict(
        boxstyle="round",
        facecolor="#1a1a2e",
        alpha=0.9,
        edgecolor="#ff6b6b",
        linewidth=2,
    ),
    color="white",
    weight="bold",
)

# Add data source
fig.text(
    0.5,
    0.02,
    "Data Source: NOAA Mauna Loa Observatory | Dr. Charles David Keeling",
    ha="center",
    fontsize=10,
    color="gray",
)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Save with high DPI
plt.savefig(
    "co2_keeling_curve.png",
    dpi=300,
    facecolor="#1a1a2e",
    edgecolor="none",
    bbox_inches="tight",
)
print("✅ Keeling Curve saved as 'co2_keeling_curve.png'")

# Display
plt.show()
