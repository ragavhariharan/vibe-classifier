import time
import joblib
import pandas as pd
import numpy as np
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    options = uc.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("--start-maximized")
    
    # Block popups
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    
    driver = uc.Chrome(options=options, version_main=146)
    return driver

driver = get_driver()
driver.get("https://tunebat.com/") # Load initially to trigger captcha

# --- 🛑 MANUAL CHECKPOINT 🛑 ---
print("\n" + "="*50)
print("🚀 BROWSER LAUNCHED!")
print("1. Go to the Chrome window.")
print("2. If you see a 'Verify you are human' box, CLICK IT.")
print("3. Wait until you see the actual Tunebat search bar.")
input("👉 Press ENTER here in the terminal once the site is ready...")
print("="*50 + "\n")

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
        wait = WebDriverWait(driver, 10)
        try:
            # Try to grab structural track links
            result_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/Info/'], .search-result-item, .row.search-result a")))
            driver.execute_script("arguments[0].click();", result_link)
        except:
            try:
                # Fallback: case-insensitive match on the first word of the song
                first_word = song_name.split(' ')[0].lower()
                xpath = f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{first_word}')]"
                link = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                driver.execute_script("arguments[0].click();", link)
            except:
                print("❌ Song not found.")
                return None
        
        # Scrape
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "attribute-energy")))
        except:
            with open('dom_track.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("❌ Stats not found (or blocked). Saved DOM to dom_track.html")
            return None
            
        def get_val_by_class(class_name, default=None):
            try:
                text = driver.find_element(By.CSS_SELECTOR, f"div[class*='{class_name}'] .current-value, div[class*='{class_name}'] div div:nth-child(2)").text
                return float(text.replace(' dB', '').strip())
            except:
                return default if default is not None else 50.0

        energy = get_val_by_class("attribute-energy")
        dance = get_val_by_class("attribute-danceability")
        happy = get_val_by_class("attribute-happiness", default=50.0) 
        loud = get_val_by_class("attribute-loudness")
        
        return energy, dance, happy, loud

    except Exception as e:
        print(f"❌ Could not find stats. ({str(e)[:50]})")
        return None

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