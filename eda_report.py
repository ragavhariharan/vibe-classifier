import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load Data
df = pd.read_csv('cleaned_dataset.csv')

# --- FIX: Re-create the missing features for the report ---
df['Intensity'] = df['Energy'] * df['Danceability']
df['Vocal_Proxy'] = df['Loudness'] / (df['Energy'] + 0.001)  # <--- This was missing!
df['Depression_Score'] = (100 - df['Happiness']) * (100 - df['Energy'])
# ----------------------------------------------------------

# 2. Summary Statistics
print("Generating Summary Stats...")
desc = df.describe()
desc.to_csv("summary_statistics.csv")
print("✅ Saved summary_statistics.csv")

# 3. Correlation Heatmap
plt.figure(figsize=(10, 8))
# Drop non-numeric columns
numeric_df = df.drop(['Song Name', 'Vibe'], axis=1)
sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Feature Correlation Matrix")
plt.savefig("correlation_heatmap.png")
print("✅ Saved correlation_heatmap.png")

# 4. Box Plots
# Energy Boxplot
plt.figure(figsize=(10, 6))
# Fixed syntax to silence warnings
sns.boxplot(x='Vibe', y='Energy', hue='Vibe', data=df, palette="husl", legend=False)
plt.title("Energy Levels by Vibe")
plt.savefig("energy_boxplot.png")
print("✅ Saved energy_boxplot.png")

# Vocal Proxy Boxplot (This will work now!)
plt.figure(figsize=(10, 6))
sns.boxplot(x='Vibe', y='Vocal_Proxy', hue='Vibe', data=df, palette="husl", legend=False)
plt.title("Vocal Proxy (Loudness/Energy) by Vibe")
plt.savefig("vocal_proxy_boxplot.png")
print("✅ Saved vocal_proxy_boxplot.png")

print("\n🎉 EDA Report Generated Successfully!")