from dotenv import load_dotenv
load_dotenv()
import os
from scrim_classes import Team

constants = {
    "DEBUG_MODE": True,
    "TEAM_LINK": "https://lol.gankster.gg/teams/107750/testingt",
    # "TEAM_LINK": "https://lol.gankster.gg/teams/84830/cryobark",
    "CHANNEL_ID": 1378457387442245702,
    "GUILD_ID": 378727445903441930,
    # "CRYOBARK_ROLE_ID": 1405677183988666410,
    # "MANAGER_ROLE_ID": 1291840665335894027,
    "CRYOBARK_ROLE_ID": 378729316990713856,
    "MANAGER_ROLE_ID": 378728545826111508,
    "TREBOTEHTREE": 306170246232801290,
    "GOOGLE_SCOPES": ["https://www.googleapis.com/auth/script.external_request", "https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/spreadsheets"],
    "ZINSKI_ODDS": .01,
    "POLL_PINGERS": [301513241807421440 ,306170246232801290, 277174048843235330, 301504795175550976, 267023049931358208, 465587770337918976],
    "ALL_MEMBERS": {301513241807421440 ,306170246232801290, 277174048843235330, 301504795175550976, 267023049931358208, 465587770337918976, 145798980016537600},
    "CRYOBARK": Team(number="84830", name="Cryobark"),
    "WILDCARD_TEAM": Team(number="-1")
}

DEBUG_MODE: bool = constants["DEBUG_MODE"]

def debugPrint(text: str):
    if DEBUG_MODE:
        print(text)

def getVariable(varName: str):
    if varName in constants:
        return constants[varName]
    return os.getenv(varName)

def ordinal(n):
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))