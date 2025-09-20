import json
import os

from dotenv import load_dotenv

from scrim_classes import Team

load_dotenv()

constants = {
    "DEBUG_MODE": True,
    "TEAM_LINK": "https://lol.gankster.gg/teams/84830/cryobark",
    "POLL_CHANNEL_ID": 1414775214616744076,
    "SCRIM_CHANNEL_ID": 1418809724022951946,
    "ERROR_CHANNEL_ID": 1418809785255465031,
    "GUILD_ID": 1291838766733852785,
    "CRYOBARK_ROLE_ID": 1405677183988666410,
    "MANAGER_ROLE_ID": 1291840665335894027,
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
    """Reads update_variables from the json file"""
    with open(UPDATE_VARIABLES, "r") as f:
        return json.load(f)

def _save_update_varaibles():
    """Writes update_variables to the json file"""
    with open(UPDATE_VARIABLES, "w") as f:
        json.dump(update_variables, f, indent=4)

update_variables = _get_update_variables()

def debugPrint(text: str):
    """Should be used instead of print to apropriatly manage what the bot logs"""
    if DEBUG_MODE:
        print(text)

def getVariable(varName: str):
    """Gets the value of a variable checking constants, update_variables, and .env in that order"""
    if varName in constants:
        return constants[varName]
    if varName in update_variables:
        return update_variables[varName]
    return os.getenv(varName)

def setVariable(varName: str, value):
    """Sets the value of a variable in the UPDATE_VARIABLES json"""
    update_variables[varName] = value
    _save_update_varaibles()

def ordinal(n):
    """Converts a number to the formated number ex. 1 to 1st"""
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))