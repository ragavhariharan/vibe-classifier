from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# 1. Setup
driver = webdriver.Chrome() 
driver.get("https://tunebat.com/")

# 2. Search
print("Searching for Blinding Lights...")
search_bar = driver.find_element(By.XPATH, "//input[@type='search' or @type='text']")
search_bar.send_keys("The Weeknd Blinding Lights")
search_bar.send_keys(Keys.RETURN)

time.sleep(4) # Wait for results

# 3. CLICK THE RESULT (The Magic Step)
# This finds the link containing the text "Blinding Lights" and clicks it.
try:
    print("Clicking the song link...")
    song_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Blinding Lights")
    song_link.click()
except:
    print("Could not click! Please click the song manually.")

time.sleep(5) # Wait for details page to load

# 4. PAUSE for Inspection
print("\n" + "="*40)
print("WE ARE NOW ON THE DETAILS PAGE!")
print("Look for the big colored bars or numbers.")
print("Right-click 'Energy' number -> Inspect")
print("Right-click 'Danceability' number -> Inspect")
print("="*40)

input("Press Enter to close browser...")
driver.quit()