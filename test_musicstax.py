import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup

options = uc.ChromeOptions()
options.add_argument("--headless=new")
driver = uc.Chrome(options=options, version_main=146)
driver.get("https://musicstax.com/search?q=beat+it")
time.sleep(5)
html = driver.page_source
with open("test_musicstax.html", "w") as f:
    f.write(html)
driver.quit()
