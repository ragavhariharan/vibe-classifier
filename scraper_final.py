import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# --- CONFIGURATION ---
FILES = {
    'Party': 'party.txt',
    'Workout': 'workout.txt',
    'Study': 'study.txt',
    'Sleep': 'sleep.txt'
}
OUTPUT_FILE = 'final_dataset.csv'

# --- 1. SETUP FUNCTIONS ---
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    # Block notifications and popups via browser preferences
    prefs = {
        "profile.default_content_setting_values.notifications": 2, 
        "profile.managed_default_content_settings.popups": 2
    }
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def get_safe_text(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text
    except:
        return "0"

def close_popups(driver):
    """Checks for new tabs, closes them, and returns to main."""
    try:
        main_window = driver.window_handles[0]
        if len(driver.window_handles) > 1:
            # print("   🛡️  Popup detected! Closing it...")
            for handle in driver.window_handles:
                if handle != main_window:
                    driver.switch_to.window(handle)
                    driver.close()
            driver.switch_to.window(main_window)
    except:
        pass # If this fails, we just keep going

# --- 2. CHECK EXISTING PROGRESS ---
processed_songs = set()
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None) 
        for row in reader:
            if row:
                processed_songs.add(row[0])

print(f"🔄 Resuming... Found {len(processed_songs)} songs already done.")

# --- 3. MAIN LOOP ---
with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    
    driver = get_driver()
    songs_since_restart = 0

    print("🚀 Starting Popup-Killer Scraper...")

    for vibe, filename in FILES.items():
        print(f"\n📂 Checking: {vibe}")
        
        try:
            with open(filename, 'r') as song_file:
                songs = [line.strip() for line in song_file.readlines() if line.strip()]
        except FileNotFoundError:
            continue

        for song in songs:
            if song in processed_songs:
                continue

            # MAINTENANCE: Restart browser every 20 songs to clear memory
            if songs_since_restart >= 20:
                print("♻️  Refreshing browser memory...")
                driver.quit()
                time.sleep(2)
                driver = get_driver()
                songs_since_restart = 0

            print(f"   🔎 Searching: {song}...", end=" ")
            
            try:
                # 1. Kill Popups before we start
                close_popups(driver)
                
                driver.get("https://tunebat.com/")
                
                # 2. Kill Popups again (Tunebat often opens one on load)
                close_popups(driver)

                # 3. Find Search Box (with Retry/Refresh Logic)
                try:
                    search_box = driver.find_element(By.XPATH, "//input[@type='search' or @type='text']")
                except:
                    # If failed, refresh page and try one more time
                    # print("   ⚠️  Search box blocked. Refreshing...")
                    driver.refresh()
                    time.sleep(3)
                    close_popups(driver)
                    search_box = driver.find_element(By.XPATH, "//input[@type='search' or @type='text']")

                search_box.clear()
                search_box.send_keys(song)
                search_box.send_keys(Keys.RETURN)
                time.sleep(2) 
                
                # 4. Click Result
                first_word = song.split(' - ')[-1].split(' ')[0]
                try:
                    link = driver.find_element(By.PARTIAL_LINK_TEXT, first_word)
                    driver.execute_script("arguments[0].scrollIntoView();", link)
                    driver.execute_script("arguments[0].click();", link)
                except:
                    # Backup Click
                    driver.find_element(By.CSS_SELECTOR, ".search-result-item").click()
                
                time.sleep(3) 
                
                # 5. Scrape
                energy = get_safe_text(driver, "//main/div/div[1]/div[4]/div/div[2]/div/div/span")
                dance = get_safe_text(driver, "//main/div/div[1]/div[4]/div/div[3]/div/div/span")
                happy = get_safe_text(driver, "//main/div/div[1]/div[4]/div/div[4]/div/div/span")
                loud = get_safe_text(driver, "//main/div/div[1]/div[4]/div/div[9]/div/div/span")
                
                if energy == "0":
                    print("❌ Failed (Got 0s)")
                else:
                    writer.writerow([song, vibe, energy, dance, happy, loud])
                    f.flush()
                    print(f"✅ Saved! (E:{energy})")
                    songs_since_restart += 1

            except Exception as e:
                print(f"❌ Error ({str(e)[:15]}...)")
                # If total crash, restart
                if "invalid session" in str(e) or "chrome not reachable" in str(e):
                    print("⚠️ Critical Crash! Rebooting...")
                    try: driver.quit()
                    except: pass
                    driver = get_driver()
                    songs_since_restart = 0

print("\n🎉 All Done!")
driver.quit()