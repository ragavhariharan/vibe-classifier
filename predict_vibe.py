import joblib
import pandas as pd
import numpy as np

# 1. Load the Brains
print("Loading model and scaler...")
try:
    model = joblib.load('spotify_vibe_model.pkl')
    scaler = joblib.load('scaler.pkl')
except FileNotFoundError:
    print("❌ Error: Make sure spotify_vibe_model.pkl and scaler.pkl are in this folder!")
    exit()

# 2. Define the Prediction Function
def predict_song_vibe(energy, danceability, happiness, loudness):
    # A. Create the input table (DataFrame)
    input_df = pd.DataFrame([[energy, danceability, happiness, loudness]], 
                            columns=['Energy', 'Danceability', 'Happiness', 'Loudness'])
    
    # B. Add the "Secret Features" (Must match training EXACTLY)
    input_df['Intensity'] = input_df['Energy'] * input_df['Danceability']
    input_df['Depression_Score'] = (100 - input_df['Happiness']) * (100 - input_df['Energy'])
    
    # C. Scale the data (Resize using the saved scaler)
    input_scaled = scaler.transform(input_df)
    
    # D. Predict
    prediction = model.predict(input_scaled)[0]
    probs = model.predict_proba(input_scaled)[0]
    classes = model.classes_
    
    # E. Print Results
    print(f"\n🔮 Result: **{prediction}**")
    print("📊 Confidence:")
    for vibe, score in zip(classes, probs):
        print(f"   - {vibe}: {score*100:.1f}%")

# 3. Start the Loop
print("\n" + "="*40)
print("🎵 Spotify Vibe Predictor Ready 🎵")
print("="*40)

while True:
    print("\n--- Enter Song Stats (type 'exit' to quit) ---")
    try:
        e_in = input("Energy (0-100): ")
        if e_in.lower() == 'exit': break
        
        e = float(e_in)
        d = float(input("Danceability (0-100): "))
        h = float(input("Happiness (0-100): "))
        l = float(input("Loudness (e.g. -5, -20): "))
        
        predict_song_vibe(e, d, h, l)
        
    except ValueError:
        print("❌ Please enter numbers only!")