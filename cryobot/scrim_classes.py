from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

class ScrimFormat(Enum):
    BEST_OF_ONE = ("Bo1", "Best of One", 1 )
    BEST_OF_TWO = ("Bo2", "Best of Two", 2)
    BEST_OF_THREE = ("Bo3", "Best of Three", 3)
    BEST_OF_FOUR = ("Bo4", "Best of Four", 4)
    BEST_OF_FIVE = ("Bo5", "Best of Five", 5)
    ONE_GAME = ("1 Game", "One Game", 1)
    TWO_GAMES = ("2 Games", "Two Games", 2)
    THREE_GAMES = ("3 Games", "Three Games", 3)
    FOUR_GAMES = ("4 Games", "Four Games", 4)
    FIVE_GAMES = ("5 Games", "Five Games", 5)
    NONE = ("None", "None", 0)

    def __init__(self, format_short: str, format_long: str, games: int):
        self.format_short = format_short
        self.format_long = format_long
        self.games = games

    def from_short(short: str): 
        for sf in ScrimFormat:
            if sf.format_short == short:
                return sf

    def from_long(long: str): 
        for sf in ScrimFormat:
            if sf.format_long == long:
                return sf

class Tier(Enum):
    IRON = "Iron"
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"
    EMERALD = "Emerald"
    DIAMOND = "Diamond"
    MASTER = "Master"
    GRANDMASTER = "Grandmaster"
    CHALLENGER = "Challenger"

class Position(Enum):
    TOP = "Top"
    JUNGLE = "Jungle"
    MIDDLE = "Middle"
    BOTTOM = "Bottom"
    SUPPORT = "Support"

@dataclass
class Rank:
    tier: Tier
    division: str
    lp: int
    wins: int
    losses: int
    positions: list[Position]

@dataclass
class Player:
    """Class representing a player on a Gankster team"""
    name: str
    rank: str
    tag: str = ""
    puuid: str = ""
    champions: list[str] = ()

@dataclass
class Reputation:
    gankRep: str = ""
    likes: str = ""
    dislikes: str = ""
    responseTime: str = ""
    responseRate: str = ""
    cancellationRate: str = ""
    communication: str = ""
    behavior: str = ""
    onTime: str = ""
    reviews: list[str] = ()

@dataclass
class Team:
    """Class representing a gankster team"""
    number: str = ""
    name: str = ""
    rank: str = "" #Team ranks are different than individual rank
    region: str = ""
    bio: str = ""
    roster: list[Player] = ()
    subs: list[Player] = ()
    opggLink: str = ""
    created: datetime = None
    reputation: Reputation = None

    def __eq__(self, other):
        if isinstance(other, Team):
            if self.number == other.number and self.number:
                return True
            if self.name == other.name and self.name:
                return True
        return False

    def __str__(self):
        return f"<Team: name='{self.name}', number={self.number}>"

    def __bool__(self):
        return bool(self.number or self.name)

@dataclass
class Scrim:
    time: datetime
    scrim_format: ScrimFormat = ScrimFormat.NONE
    team: Team = None
    open: bool = True

    def __eq__(self, other):
        if isinstance(other, Scrim):
            return self.time == other.time and self.scrim_format == other.scrim_format
        return False

    def __hash__(self):
        return hash((self.time, self.scrim_format))

    def __str__(self):
        return f"<Scrim: time='{self.time.strftime('%m/%d/%y %I:%M %p')}', format='{self.scrim_format.format_short}', team={str(self.team)}, open={self.open}>"

    def get_scrim_end_time(self):
        return self.time + timedelta(hours=self.scrim_format.games)

    def get_gankster_removal_time(self):
        return self.time + timedelta(minutes=(40 * self.scrim_format.games))


    # def __repr__(self):
    #     return f"<Scrim {self.scrim_format.name} at {self.date_time}>"

class ErrorName(Enum):
    NONE = "None"
    UNKNOWN = "Unknown"
    AUTH_NOT_SETUP = "AuthNotSetup"
    TEAM_NAME_NULL = "TeamNameNull"
    TEAM_NUMBER_NULL = "TeamNumberNull"
    DATE_NULL = "DateNull"
    FORMAT_NULL = "FormatNull"
    INVALID_DATE = "InvalidDate"
    NO_NEW_TEAM_X = "NoNewTeamX"
    INVALID_CANCEL_TEAM = "InvalidCancelTeam"
    INVALID_CANCEL_DATE = "InvalidCancelDate"
    INVALID_CBK_PLAYERS = "InvalidCBKPlayers"
    INVALID_CBK_CHAMPS = "InvalidCBKChamps"
    INVALID_CBK_PICK_ORDER = "InvalidCBKPickOrder"
    INVALID_ENEMY_CHAMPS = "InvalidEnemyChamps"
    INVALID_ENEMY_PICK_ORDER = "InvalidEnemyPickOrder"
    MISSING_CRYOBARK_SIDE_NAME = "MissingCryobarkSideName"
    MISSING_ENEMY_SIDE_NAME = "MissingEnemySideName"
    INCORRECT_ENEMY_SIDE_NAME = "IncorrectEnemySideName"
    INVALID_TEAM_NAME = "InvalidTeamName"
    MISSING_TEAM_NUMBER = "MissingTeamNumber"
    INVALID_TEAM_NUMBER = "InvalidTeamNumber"
    INVALID_CHAMP_NAME = "InvalidChampName"
    INVALID_BLUE_PICK_ORDER = "InvalidBluePickOrder"
    INVALID_RED_PICK_ORDER = "InvalidRedPickOrder"
    MISSING_BLUE_ROUND_ONE_BANS = "MissingBlueRoundOneBans"
    MISSING_BLUE_ROUND_TWO_BANS = "MissingBlueRoundTwoBans"
    MISSING_RED_ROUND_ONE_BANS = "MissingRedRoundOneBans"
    MISSING_RED_ROUND_TWO_BANS = "MissingRedRoundTwoBans"
    ALREADY_REVIEWED_SCRIM_BLOCK = "AlreadyReviewedScrimBlock"
    INVALID_GAME_COUNT = "InvalidGameCount"
    INVALID_GAME_RECORD = "InvalidGameRecord"
    INVALID_BLOCK_FORMAT = "InvalidBlockFormat"
    MISSING_GAME_RECORD = "MissingGameRecord"
    SCOUTING_TEAM_NOT_FOUND = "ScoutingTeamNotFound"
    NO_TEAM_OUTGOING_SCRIM_REQUEST = "NoTeamOutgoingScrimRequest"
    SCRIM_REQUEST_NOT_FOUND = "ScrimRequestNotFound"
    GANKSTER_UNAVAILIBLE = "GanksterUnavailible"
    NO_SCRIM_BLOCK_FOUND = "NoScrimBlockFound"
    GANKSTER_FAILED = "GanksterFailed"

ERROR_DESCRIPTIONS = {
    ErrorName.NONE: "No Issue",
    ErrorName.UNKNOWN: "No clue what went wrong",
    ErrorName.AUTH_NOT_SETUP: "Auth Not Setup On Raspberry Pi",
    ErrorName.TEAM_NAME_NULL: "Team name is missing",
    ErrorName.TEAM_NUMBER_NULL: "Team number is missing",
    ErrorName.DATE_NULL: "Date is missing",
    ErrorName.FORMAT_NULL: "Format is missing",
    ErrorName.INVALID_DATE: "Date format is invalid",
    ErrorName.NO_NEW_TEAM_X: "No NewTeamX availible in Scouting Report, please create one",
    ErrorName.INVALID_CANCEL_TEAM: "Team not found for the given scrim day",
    ErrorName.INVALID_CANCEL_DATE: "No scrim page found for the given date",
    ErrorName.INVALID_CBK_PLAYERS: "Cryobark players list is the wrong size",
    ErrorName.INVALID_CBK_CHAMPS: "Cryobark champions list is the wrong size",
    ErrorName.INVALID_CBK_PICK_ORDER: "Cryobark pick order list is the wrong size",
    ErrorName.INVALID_ENEMY_CHAMPS: "Enemy champions list is the wrong size",
    ErrorName.INVALID_ENEMY_PICK_ORDER: "Enemy pick order list is the wrong size",
    ErrorName.MISSING_CRYOBARK_SIDE_NAME: "The side Cryobark is on is missing for the given game",
    ErrorName.MISSING_ENEMY_SIDE_NAME: "The side the enemy team is on is missing for the given game",
    ErrorName.INCORRECT_ENEMY_SIDE_NAME: "The side the enemy team is on is incorrecetly named for the given game",
    ErrorName.INVALID_TEAM_NAME: "The given team name conflicts with the days results for the given day",
    ErrorName.MISSING_TEAM_NUMBER: "The given team name is not found in the scouting report",
    ErrorName.INVALID_TEAM_NUMBER: "The provided team number in the scrim results doesn't match the scouting document",
    ErrorName.INVALID_CHAMP_NAME: "Champion name is either misspelled or improperly capitalized/formatted",
    ErrorName.INVALID_BLUE_PICK_ORDER: "Blue team pick order is wrong",
    ErrorName.INVALID_RED_PICK_ORDER: "Red team pick order is wrong",
    ErrorName.MISSING_BLUE_ROUND_ONE_BANS: "Blue team round one bans are missing (check completed checkbox if intended)",
    ErrorName.MISSING_BLUE_ROUND_TWO_BANS: "Blue team round two bans are missing (check completed checkbox if intended)",
    ErrorName.MISSING_RED_ROUND_ONE_BANS: "Red team round one bans are missing (check completed checkbox if intended)",
    ErrorName.MISSING_RED_ROUND_TWO_BANS: "Red team round two bans are missing (check completed checkbox if intended)",
    ErrorName.ALREADY_REVIEWED_SCRIM_BLOCK: "Scrim block has already been reviewed",
    ErrorName.INVALID_GAME_COUNT: "Game count is invalid for the given date",
    ErrorName.INVALID_GAME_RECORD: "Game record is unobtanable for the given format and date",
    ErrorName.INVALID_BLOCK_FORMAT: "Scrim block format is invalid",
    ErrorName.MISSING_GAME_RECORD: "Game record is missing for the given date",
    ErrorName.SCOUTING_TEAM_NOT_FOUND: "Team was not found in scouting report when attempting update",
    ErrorName.NO_TEAM_OUTGOING_SCRIM_REQUEST: "The given team did not have an outgoing scrim request so I can't send a scrim request",
    ErrorName.SCRIM_REQUEST_NOT_FOUND: "There was no scrim request matching the provided scrim found within the notifications to accept/decline",
    ErrorName.GANKSTER_UNAVAILIBLE: "Gankster is down at the moment, please try again later",
    ErrorName.NO_SCRIM_BLOCK_FOUND: "Could not find the given scrim block sceduled for team Cryobark",
    ErrorName.GANKSTER_FAILED: "The given function's success condition failed to be met"
}

@dataclass
class CryoBotError(Exception):
    name: ErrorName
    fields: str
    description: Optional[str] = None

    def __post_init__(self):
        if self.description is None:
            self.description = ERROR_DESCRIPTIONS[self.name]

    def __str__(self):
        if self.name == ErrorName.UNKNOWN:
            return f"CryoBotError: ({self.description})"
        return f"CryoBotError: ({self.name.value}: {self.description} | fields=[{self.fields}])"