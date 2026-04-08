import time
import random
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
FILES = {
    'Party': 'party.txt',
    'Workout': 'workout.txt',
    'Sleep': 'sleep.txt',
    'Study': 'study.txt'
}
CSV_FILE = 'final_dataset.csv'

# --- 1. SETUP BROWSER ---
def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Allow popups (sometimes needed for search to work)
    prefs = {"profile.default_content_setting_values.notifications": 1}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

# --- 2. SCRAPER FUNCTION ---
def get_song_stats(driver, song_name, wait):
    print(f"   🔎 Searching: {song_name}...", end=" ", flush=True)
    try:
        # A. Go to Home (Only if not already there to save time)
        if "tunebat.com" not in driver.current_url:
            driver.get("https://tunebat.com/")
        
        # B. Smart Wait for Search Box (Max 10 seconds)
        try:
            search_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='search'], input[type='text']")))
        except:
            # If search box missing, try refreshing once
            driver.refresh()
            time.sleep(4)
            search_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='search'], input[type='text']")))

        # C. Search
        search_box.clear()
        search_box.send_keys(song_name)
        search_box.send_keys(Keys.RETURN)
        
        # D. Wait for Results & Click
        try:
            # Wait for EITHER the result link OR the "No results" text
            result_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".search-result-item, .row.search-result a")))
            result_link.click()
        except:
            print("❌ Song not found (or blocked).")
            return None
        
        # E. Scrape Stats
        # Wait for the Energy bar to appear (confirms page loaded)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "attribute-energy")))
        
        def get_val(class_name):
            # Find the value inside the attribute div
            text = driver.find_element(By.CSS_SELECTOR, f"div[class*='{class_name}'] .current-value, div[class*='{class_name}'] div div:nth-child(2)").text
            return text.replace(' dB', '').strip()

        energy = get_val("attribute-energy")
        dance = get_val("attribute-danceability")
        happy = get_val("attribute-happiness")
        loud = get_val("attribute-loudness")
        
        print(f"✅ Saved! (E:{energy})")
        return [song_name, energy, dance, happy, loud]

    except Exception as e:
        # TAKE A SCREENSHOT ON FAILURE
        driver.save_screenshot("debug_error.png")
        print(f"❌ Error: {str(e)[:30]}... (Screenshot saved)")
        return None

# --- 3. MAIN LOOP ---
driver = get_driver()
wait = WebDriverWait(driver, 10) # 10 second timeout

# --- 🛑 MANUAL CHECKPOINT 🛑 ---
print("\n" + "="*50)
print("🚀 BROWSER LAUNCHED!")
print("1. Go to the Chrome window.")
print("2. If you see a 'Verify you are human' box, CLICK IT.")
print("3. If you see a Cookie Banner, CLOSE IT.")
print("4. Make sure you can see the Search Bar.")
input("👉 Press ENTER here in the terminal once the site is ready...")
print("="*50 + "\n")

# Load existing data
existing_songs = set()
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row:
                existing_songs.add(row[0])

# Prepare CSV
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Song Name', 'Energy', 'Danceability', 'Happiness', 'Loudness', 'Vibe'])

try:
    for vibe, filename in FILES.items():
        print(f"\n📂 Checking: {vibe}")
        if not os.path.exists(filename): continue
            
        with open(filename, 'r', encoding='utf-8') as f:
            songs = [line.strip() for line in f.readlines() if line.strip()]
        
        for song in songs:
            if song in existing_songs:
                continue 

            stats = get_song_stats(driver, song, wait)
            
            if stats:
                stats.append(vibe)
                with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(stats)
                existing_songs.add(song)
                
                # Sleep to be safe (random 4-7 seconds)
                time.sleep(random.uniform(4, 7))
            else:
                # If failed, wait longer before trying next song
                time.sleep(5)

except KeyboardInterrupt:
    print("\n🛑 Stopped by user.")
finally:
    driver.quit()