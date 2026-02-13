import pandas as pd

# 1. Load your raw data
print("Loading raw data...")
try:
    df = pd.read_csv('final_dataset.csv')
except FileNotFoundError:
    print("❌ Error: 'final_dataset.csv' not found. Did you run the scraper?")
    exit()

# 2. Drop the failed rows (The "Zeros")
# We remove any row where Energy is exactly 0
initial_count = len(df)
df = df[df['Energy'] != 0]
dropped_count = initial_count - len(df)
print(f"Dropped {dropped_count} failed songs (zeros).")

# 3. Fix the "Loudness" column (Remove ' dB')
# This forces the column to be a string, replaces ' dB', then converts to a number
# We use 'errors=coerce' to turn any unreadable text into NaN, then drop those
df['Loudness'] = df['Loudness'].astype(str).str.replace(' dB', '', regex=False)
df['Loudness'] = pd.to_numeric(df['Loudness'], errors='coerce')

# 4. Drop any rows that still have NaN values (just to be safe)
df.dropna(inplace=True)

# 5. Check for duplicates
df = df.drop_duplicates(subset=['Song Name'])

# 6. Save the clean version
df.to_csv('cleaned_dataset.csv', index=False)

print("\nSUCCESS! ✨")
print(df.head())
print(f"\nSaved clean data to 'cleaned_dataset.csv' with {len(df)} songs.")