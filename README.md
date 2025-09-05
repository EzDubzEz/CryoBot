# Cryobot
Cryobark Discord Bot

# TODO:
- Setup gankster api calls to retrieve_incoming_scrim_requests (without team information), fill_team_stats, and fill_player_stats
- Look into gankster api cookies to retrieve_incoming_scrim_requests (with team information), scrims listed, incoming scrim requests, etc. whatever is possible 
- Setup Selenium to scrape scrim team information for the bot to use and navigate gankster scrim creation etc.

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