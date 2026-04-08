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
import urllib.parse

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

# --- 🛑 MANUAL CHECKPOINT 🛑 ---
print("\n" + "="*50)
print("🚀 NOTE: Chrome will launch for each search to clear its memory.")
print("If you hit Cloudflare, simply click 'Verify you are human'.")
print("="*50 + "\n")

def close_popups(driver):
    """Closes any extra tabs that Tunebat opens."""
    try:
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    except:
        pass

def get_song_stats(song_name):
    print(f"\n🔎 Booting isolated Scraper for '{song_name}'...")
    driver = None
    try:
        driver = get_driver()
        
        # Initial ping to bypass stealth checks smoothly
        driver.get("https://tunebat.com/")
        time.sleep(2)
        close_popups(driver)
        
        # Bypass the Tunebat search box UI entirely, routing directly via URL
        search_url = f"https://tunebat.com/Search?q={urllib.parse.quote(song_name)}"
        driver.get(search_url)
        wait = WebDriverWait(driver, 10)
        
        # Click
        try:
            result_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/Info/'], .search-result-item, .row.search-result a")))
            driver.execute_script("arguments[0].click();", result_link)
        except:
            try:
                first_word = song_name.split(' ')[0].lower()
                xpath = f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{first_word}')]"
                link = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                driver.execute_script("arguments[0].click();", link)
            except:
                print("❌ Song not found.")
                return None
        
        # Scrape
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-progress-text")))
            time.sleep(1.5) # Crucial: Allow React to finish injecting the typography labels AFTER circles render!
        except:
            with open('dom_track.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("❌ Stats not found (or blocked). Saved DOM to dom_track.html")
            return None
            
        def get_val_by_text(label_text, default=None):
            try:
                # 1. Fetch all spans on the page
                spans = driver.find_elements(By.TAG_NAME, "span")
                
                # 2. Pythonically locate the label text to bypass messy XPATH translate() functions
                target_span = None
                for s in spans:
                    if s.text and label_text.lower() == s.text.lower().strip():
                        target_span = s
                        break
                        
                if not target_span:
                    raise Exception(f"Visual label span not injected by React yet.")
                    
                # 3. Walk up to parent wrapper, then dig down to the digit
                parent_wrapper = target_span.find_element(By.XPATH, "..")
                digit_span = parent_wrapper.find_element(By.CSS_SELECTOR, ".ant-progress-text")
                return float(digit_span.text.replace(' dB', '').replace('%', '').strip())
                
            except Exception as e:
                print(f"⚠️ Warning: Could not scrape '{label_text}'. Using default {default}. Error: {e}")
                return default if default is not None else 50.0

        energy = get_val_by_text("energy")
        dance = get_val_by_text("danceability")
        happy = get_val_by_text("happiness", default=50.0) 
        loud = get_val_by_text("loudness", default=-6.0)
        
        return energy, dance, happy, loud

    except Exception as e:
        print(f"❌ Error analyzing song: ({str(e)[:50]})")
        return None
    finally:
        if driver:
            driver.quit()

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
