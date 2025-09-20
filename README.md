# Cryobot
Cryobark Discord Bot

# TODO:
- Look into adding to google script to get stats to do stuff (retrieve team scrim history, retrieve winrate, various queries, etc.)

# Selenium Setup
- You need to manually log into gankster for chrome, and gankster/google/riot don't let you log in if selenium opens the browser so that must be done manually aswell
- Run Selenium.py and create the Selenium class at least once so the ChromeProfile folder is created in the CryoBot directory
- Open command prompt and run the command 
- - & "C:\Program Files\Google\Chrome\Application\chrome.exe" '--profile-directory=Default' '--user-data-dir="<ChromeProfileDirectory\>"' 
- - replacing <ChromeProfileDirectory\> with the ChromeProfile absolute file path ex. "C:\Users\Trevor\OneDrive\Documents\Code\CryoBot\ChromeProfile"
- Log into gankster and **choose remember me**
- Click view site information button (leftmost of browser search)
- Allow notifications in site settings (prevents a popup) 
- Close the window

- Download chromedriver from [here](https://googlechromelabs.github.io/chrome-for-testing/) matching your chrome version and save it to a folder
- Add folder to System Variables -> Path

# Google API Setup
- Run google_api.py as main
- In the newly opened browser window allow the selected permissions