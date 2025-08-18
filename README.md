# Cryobot
Cryobark Discord Bot

# TODO:
- Send a poll every saturday night for the next week
- Track when we get a scrim pending/confimred and sending messages in chat
- Look into Selenium/etc. to scrape scrim team information for the bot to use
- Call the cryobark google API to create the scouting doc and update scrim results sheet

# Selenium Setup
- You need to manually log into gankster for chrome, and gankster/google/riot don't let you log in if selenium opens the browser so that must be done manually aswell
- Run Selenium.py and create the Selenium class at least once so the ChromeProfile folder is created in the CryoBot directory
- Open command prompt and run the command "& 'C:\Program Files\Google\Chrome\Application\chrome.exe' --user-data-dir='\<ChromeProfileDirectory\>'" replacing \<ChromeProfileDirectory\> with the ChromeProfile absolute file path ex. "C:\Users\Trevor\OneDrive\Documents\Code\CryoBot\ChromeProfile"
- Log into gankster and **choose remember me**
- Close the window
