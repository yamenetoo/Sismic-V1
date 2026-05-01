# This code provides a complete workflow for seismic catalog completeness analysis using the SeismoStats library. It begins by loading and cleaning a pandas DataFrame of earthquake data, renaming columns to standard formats, filtering out invalid magnitudes and missing values, and summarizing the dataset. Next, it creates a SeismoStats Catalog object, configures magnitude binning, and estimates the Magnitude of Completeness (Mc) via the Maximum Curvature method. It then extracts magnitudes above Mc, calculates the b-value if sufficient data is available, and visualizes the cumulative frequency-magnitude distribution with a vertical line indicating Mc. This analysis helps assess the reliability of seismic catalogs for statistical modeling. [Placeholder: Expand with detailed explanations, assumptions, and usage notes for the article.]
# ==================================================
# COMPLETE CODE FOR CATALOG COMPLETENESS ANALYSIS
# ==================================================

import pandas as pd
import matplotlib.pyplot as plt
from seismostats import Catalog
from seismostats.analysis import estimate_b

# --------------------------------------------------
# 1. Load and prepare your DataFrame
# --------------------------------------------------
# Assuming your original DataFrame is named 'df'
df_clean = df.copy()

# Rename columns to match SeismoStats standards
df_clean.rename(columns={
    'MAG': 'magnitude',
    'datetime': 'time'
}, inplace=True)

# Ensure 'time' is a datetime format
df_clean['time'] = pd.to_datetime(df_clean['time'])

# Clean the data: remove magnitude <= 0 entries and any rows with missing essential data
df_clean = df_clean[df_clean['magnitude'] > 0].copy()
df_clean = df_clean.dropna(subset=['magnitude', 'time', 'LAT', 'LON'])

print(f"Original catalog size: {len(df)}")
print(f"After cleaning (MAG > 0): {len(df_clean)} events")
print(f"Magnitude range: {df_clean['magnitude'].min():.2f} – {df_clean['magnitude'].max():.2f}")

# --------------------------------------------------
# 2. Create and configure the SeismoStats Catalog
# --------------------------------------------------
cat = Catalog(df_clean)

# Set the magnitude bin width (affects other methods)
cat.delta_m = 0.1

# Round magnitudes to the nearest bin
cat.bin_magnitudes(inplace=True)

# --------------------------------------------------
# 3. Estimate Magnitude of Completeness (Mc)
# --------------------------------------------------
# Estimate Mc using the Maximum Curvature method
# Best practice: store the returned tuple to avoid a deprecation warning
best_mc, mc_info = cat.estimate_mc_maxc(fmd_bin=0.1)

# The 'mc' attribute is automatically updated
mc_maxc = cat.mc
print(f"\nMc (Maximum Curvature) = {mc_maxc:.2f}")

# --------------------------------------------------
# 4. Extract magnitudes above Mc and calculate b-value
# --------------------------------------------------
# The Catalog itself behaves like a DataFrame, so we can use direct indexing
mags_above_mc = cat[cat['magnitude'] >= mc_maxc]['magnitude']

# Check if we have enough data for a reliable b-value estimate
if len(mags_above_mc) >= 10:
    # Ensure delta_m and mc are passed correctly
    b_val = estimate_b(magnitudes=mags_above_mc, delta_m=cat.delta_m, mc=mc_maxc)
    print(f"b-value (for M ≥ {mc_maxc:.2f}): {b_val:.3f}")
else:
    print(f"\nNot enough events above Mc ({mc_maxc:.2f}) to estimate b-value.")

# --------------------------------------------------
# 5. Visualize the result
# --------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 6))
cat.plot_cum_fmd(fmd_bin=0.1, ax=ax)
ax.axvline(mc_maxc, color='red', linestyle='--', linewidth=2, label=f'Mc = {mc_maxc:.2f}')
ax.set_title('Cumulative Frequency-Magnitude Distribution (FMD)', fontsize=14)
ax.set_xlabel('Magnitude', fontsize=12)
ax.set_ylabel('Cumulative Number of Events (≥ M)', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()
