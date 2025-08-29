from dotenv import load_dotenv
load_dotenv()
import os

constants = {
    "DEBUG_MODE": True,
    "TEAM_LINK": "https://lol.gankster.gg/teams/84830/cryobark",
    "CHANNEL_ID": "1378457387442245702",
    "GUILD_ID": "378727445903441930",
    "CRYOBARK_ROLE_ID": "1405677183988666410",
    "MANAGER_ROLE_ID": "1291840665335894027",
    "GOOGLE_SCOPES": ["https://www.googleapis.com/auth/script.external_request", "https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/spreadsheets"],
    "ZINSKI_ODDS": .01,
}

DEBUG_MODE = constants["DEBUG_MODE"]

def debugPrint(text: str):
    if DEBUG_MODE:
        print(text)

def getVariable(varName: str):
    if varName in constants:
        return constants[varName]
    return os.getenv(varName)