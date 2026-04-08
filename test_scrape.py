import undetected_chromedriver as uc
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

options = uc.ChromeOptions()
options.add_argument("--headless")
driver = uc.Chrome(options=options, version_main=146)
driver.get("https://tunebat.com/Search?q=chella%20magale")
time.sleep(8)
with open('dom.html', 'w') as f:
    f.write(driver.page_source)
driver.quit()
