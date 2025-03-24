import pandas as pd
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# 📂 Load data from JSON file
json_file = "nba_data.json"

# ✅ Check if JSON file exists
if os.path.exists(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)
else:
    print("⚠️ No cached data found. Please run the data fetching script first.")
    data = []

# ✅ Convert JSON to DataFrame
df = pd.DataFrame(data)

# ✅ Convert "Actual Points" column to numeric (handle "N/A" values)
df["Actual Points"] = pd.to_numeric(df["Actual Points"], errors="coerce")  # Converts "N/A" to NaN

# ✅ Convert expected points to numeric
df["Expected Points (Book)"] = pd.to_numeric(df["Expected Points (Book)"], errors="coerce")
df["Expected Points (Fair)"] = pd.to_numeric(df["Expected Points (Fair)"], errors="coerce")

# ✅ Remove cancelled games
df = df[df["Cancelled"] == False]

# 🚀 **NEW**: Remove games where player did NOT play (Actual Points is NaN)
df = df[df["Actual Points"].notna()]

# ✅ Get unique players
players = df["Player"].unique()

# 🎨 Apply Sleeper-Style Dark Theme
plt.style.use("dark_background")
sns.set_theme(style="darkgrid")

# ✅ Define PDF output file
output_pdf = "nba_player_performance.pdf"

# ✅ Create PDF with multiple pages
with PdfPages(output_pdf) as pdf:
    num_players = len(players)
    players_per_page = 4  # Set 4 graphs per page
    num_pages = (num_players // players_per_page) + (num_players % players_per_page > 0)

    for page in range(num_pages):
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))  # 2x2 layout per page
        axes = axes.flatten()  # Flatten for easy iteration

        start_idx = page * players_per_page
        end_idx = min(start_idx + players_per_page, num_players)
        
        for i, player in enumerate(players[start_idx:end_idx]):
            ax = axes[i]
            player_df = df[df["Player"] == player].sort_values("Date")

            if player_df.empty:
                print(f"⚠️ Skipping {player} due to missing data.")
                continue

            x_labels = player_df["Date"].values
            x_data = np.arange(len(player_df))
            actual_points = player_df["Actual Points"].values
            projected_points = player_df["Expected Points (Book)"].values  # Assume Book Odds are projections

            # 🚀 Remove NaN values
            valid_mask = np.isfinite(actual_points) & np.isfinite(projected_points)
            x_data = x_data[valid_mask]
            actual_points = actual_points[valid_mask]
            projected_points = projected_points[valid_mask]

            if len(actual_points) == 0:
                print(f"⚠️ Skipping {player} due to missing or invalid values.")
                continue

            # 🎨 Determine colors: If actual > projected, make projected red, else gray
            bar_colors = ["red" if actual > proj else "#A0A0A0" for actual, proj in zip(actual_points, projected_points)]

            # 🎨 Create Sleeper-Style Bar Chart
            width = 0.6
            bars_proj = ax.bar(x_data, projected_points, width, color=bar_colors, alpha=0.6, edgecolor="black", label="Projected", zorder=2)
            bars_actual = ax.bar(x_data, actual_points, width, color="#00D1FF", alpha=0.8, edgecolor="black", label="Final", zorder=3)

            # ✏️ Add value labels
            for bars in [bars_actual, bars_proj]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width() / 2, height + 1, f"{int(height)}",
                                ha='center', va='bottom', fontsize=8, fontweight="bold")

            # Formatting
            ax.set_xticks(x_data)
            ax.set_xticklabels(x_labels, rotation=30, fontsize=8, fontweight="bold")
            ax.set_ylabel("Points", fontsize=10, fontweight="bold")
            ax.set_title(f"{player} - Performance Trend", fontsize=12, fontweight="bold")
            ax.legend(loc="upper left", fontsize=8)
            ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=1)

        # Remove empty subplots if there are less than 4 players on the page
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        # ✅ Save the current page to the PDF
        fig.tight_layout()
        pdf.savefig(fig, dpi=300, bbox_inches="tight")
        plt.close(fig)

print(f"📁 Graphs saved as: {output_pdf}")
