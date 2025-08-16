from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Optional: specify the path to chromedriver if not in PATH
# service = Service(executable_path="C:/path/to/chromedriver.exe")
# driver = webdriver.Chrome(service=service)

options = Options()
options.add_argument("--start-maximized")
# options.add_argument(r"--user-data-dir=C:\Users\Trevor\AppData\Local\Google\Chrome\User Data")
options.add_argument(r"--user-data-dir=C:/Temp/ChromeProfile")
options.add_argument("--profile-directory=Default")

driver = webdriver.Chrome(options=options)
driver.get("https://lol.gankster.gg/teams/84830/cryobark")
input()
# Wait a bit so you can see the page open
# time.sleep(10)

driver.quit()