from dotenv import load_dotenv
load_dotenv()
import os
import json

from scrim_classes import Team

constants = {
    "DEBUG_MODE": True,
    "TEAM_LINK": "https://lol.gankster.gg/teams/84830/cryobark",
    "POLL_CHANNEL_ID": 1414775214616744076,
    "SCRIM_CHANNEL_ID": 1418809724022951946,
    "ERROR_CHANNEL_ID": 1418809785255465031,
    # "GUILD_ID": 378727445903441930,  # Testing Variable
    "GUILD_ID": 1291838766733852785,
    "CRYOBARK_ROLE_ID": 1405677183988666410,
    "MANAGER_ROLE_ID": 1291840665335894027,
    # "CRYOBARK_ROLE_ID": 378729316990713856, # Testing Variable
    # "MANAGER_ROLE_ID": 378728545826111508, # Testing Variable
    "TREBOTEHTREE": 306170246232801290,
    "GOOGLE_SCOPES": ["https://www.googleapis.com/auth/script.external_request", "https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/spreadsheets"],
    "ZINSKI_ODDS": .01,
    "POLL_PINGERS": [301513241807421440 ,306170246232801290, 277174048843235330, 301504795175550976, 267023049931358208, 465587770337918976],
    "ALL_MEMBERS": {301513241807421440 ,306170246232801290, 277174048843235330, 301504795175550976, 267023049931358208, 465587770337918976, 145798980016537600},
    "CRYOBARK": Team(number=84830, name="Cryobark"),
    "WILDCARD_TEAM": Team(number=-1),
    "UPDATE_VARIABLES": "update_vars.json"
}

DEBUG_MODE: bool = constants["DEBUG_MODE"]
UPDATE_VARIABLES: str = constants["UPDATE_VARIABLES"]

def _get_update_variables():
    with open(UPDATE_VARIABLES, "r") as f:
        return json.load(f)

def _save_update_varaibles():
    with open(UPDATE_VARIABLES, "w") as f:
        json.dump(update_variables, f, indent=4)

update_variables = _get_update_variables()

def debugPrint(text: str):
    if DEBUG_MODE:
        print(text)

def getVariable(varName: str):
    if varName in constants:
        return constants[varName]
    if varName in update_variables:
        return update_variables[varName]
    return os.getenv(varName)

def setVariable(varName: str, value):
    update_variables[varName] = value
    _save_update_varaibles()

def ordinal(n):
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))