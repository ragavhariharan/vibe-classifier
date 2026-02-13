import time
import joblib
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# --- LOAD THE COMMITTEE ---
print("🧠 Loading the Committee...")
try:
    model = joblib.load('spotify_vibe_model.pkl')
    scaler = joblib.load('scaler.pkl')
except:
    print("❌ Error: Model files not found!")
    exit()

# --- SETUP BROWSER ---
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    # Block popups
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

driver = get_driver()

def close_popups():
    """Closes any extra tabs that Tunebat opens."""
    try:
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    except:
        pass

def get_song_stats(song_name):
    print(f"🔎 Searching Tunebat for '{song_name}'...")
    try:
        driver.get("https://tunebat.com/")
        close_popups()
        
        # Search
        try:
            search_box = driver.find_element(By.XPATH, "//input[@type='search' or @type='text']")
        except:
            driver.refresh()
            time.sleep(2)
            search_box = driver.find_element(By.XPATH, "//input[@type='search' or @type='text']")
            
        search_box.clear()
        search_box.send_keys(song_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        
        # Click
        try:
            first_word = song_name.split(' ')[0]
            link = driver.find_element(By.PARTIAL_LINK_TEXT, first_word)
            driver.execute_script("arguments[0].click();", link)
        except:
            driver.find_element(By.CSS_SELECTOR, ".search-result-item").click()
        
        time.sleep(3)
        
        # Scrape
        def get_val(xpath):
            text = driver.find_element(By.XPATH, xpath).text
            return float(text.replace(' dB', '').strip())

        energy = get_val("//main/div/div[1]/div[4]/div/div[2]/div/div/span")
        dance = get_val("//main/div/div[1]/div[4]/div/div[3]/div/div/span")
        happy = get_safe_val("//main/div/div[1]/div[4]/div/div[4]/div/div/span") # Use safe val
        loud = get_val("//main/div/div[1]/div[4]/div/div[9]/div/div/span")
        
        return energy, dance, happy, loud

    except Exception as e:
        print(f"❌ Could not find stats. ({str(e)[:50]})")
        return None

def get_safe_val(xpath):
    try:
        text = driver.find_element(By.XPATH, xpath).text
        return float(text.replace(' dB', '').strip())
    except:
        return 50.0 # Default if missing

def predict_vibe(energy, dance, happy, loud):
    # A. Create DataFrame
    df = pd.DataFrame([[energy, dance, happy, loud]], 
                      columns=['Energy', 'Danceability', 'Happiness', 'Loudness'])
    
    # B. Engineer Features (MUST MATCH TRAINING EXACTLY)
    df['Intensity'] = df['Energy'] * df['Danceability']
    # The new feature!
    df['Vocal_Proxy'] = df['Loudness'] / (df['Energy'] + 0.001) 
    df['Depression_Score'] = (100 - df['Happiness']) * (100 - df['Energy'])
    
    # C. Scale
    scaled_data = scaler.transform(df)
    
    # D. Predict
    prediction = model.predict(scaled_data)[0]
    probs = model.predict_proba(scaled_data)[0]
    
    print("\n" + "="*40)
    print(f"🎶 Stats: Energy={int(energy)} | Dance={int(dance)} | Loud={loud}")
    print(f"🔮 THE COMMITTEE SAYS: **{prediction.upper()}**")
    print("="*40)
    
    # Show the votes
    for vibe, score in zip(model.classes_, probs):
        bar = "█" * int(score*20)
        print(f"{vibe.ljust(8)}: {bar} {int(score*100)}%")

# --- MAIN LOOP ---
print("\n🎵 Vibe Predictor Ready! (Type 'exit' to quit)")
while True:
    user_song = input("\nEnter song name: ")
    if user_song.lower() == 'exit': break
    
    stats = get_song_stats(user_song)
    
    if stats:
        predict_vibe(*stats)

driver.quit()