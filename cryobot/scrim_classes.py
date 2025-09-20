from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

class ScrimFormat(Enum):
    """Enum representing possible gankster scrim formats"""
    BEST_OF_ONE = ("Bo1", "Best of One", "BO1", 1)
    BEST_OF_TWO = ("Bo2", "Best of Two", "BO2", 2)
    BEST_OF_THREE = ("Bo3", "Best of Three", "BO3", 3)
    BEST_OF_FOUR = ("Bo4", "Best of Four", "BO4", 4)
    BEST_OF_FIVE = ("Bo5", "Best of Five", "BO5", 5)
    ONE_GAME = ("1 Game", "One Game", "G1", 1)
    TWO_GAMES = ("2 Games", "Two Games", "G2", 2)
    THREE_GAMES = ("3 Games", "Three Games", "G3", 3)
    FOUR_GAMES = ("4 Games", "Four Games", "G4", 4)
    FIVE_GAMES = ("5 Games", "Five Games", "G5", 5)
    NONE = ("None", "None", "None", 0)

    def __init__(self, format_short: str, format_long: str, gankster_format, games: int):
        self.format_short = format_short
        self.format_long = format_long
        self.games = games
        self.gankster_format = gankster_format

    @staticmethod
    def from_short(format_short: str):
        for sf in ScrimFormat:
            if sf.format_short == format_short:
                return sf

    @staticmethod
    def from_long(format_long: str):
        for sf in ScrimFormat:
            if sf.format_long == format_long:
                return sf

    @staticmethod
    def from_gankster_format(gankster_format: str):
        for sf in ScrimFormat:
            if sf.gankster_format == gankster_format:
                return sf

class Tier(Enum):
    """Enum representing the different lol ranked tiers"""
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
    """Enum representing the different lol positions"""
    TOP = "Top"
    JUNGLE = "Jungle"
    MIDDLE = "Middle"
    BOTTOM = "Bottom"
    SUPPORT = "Support"

@dataclass
class Rank:
    """Class representing a League of Legends rank"""
    tier: Tier
    division: str
    lp: int
    wins: int
    losses: int
    positions: list[Position]

@dataclass
class Champion:
    """Class representing a player on a Gankster team"""
    name: str
    level: int = 0
    points: int = 0
    image_url: str = ""

@dataclass
class Player:
    """Class representing a player on a Gankster team"""
    name: str
    rank: str
    tag: str = ""
    puuid: str = ""
    server: str = "" # NA, EUW, etc
    champions: list[Champion] = ()
    is_sub: bool = False
    last_updated: datetime = None

    def copy(self, other):
        if isinstance(other, Player):
            self.name = other.name
            self.rank = other.rank
            self.tag = other.tag
            self.puuid = other.puuid
            self.server = other.server
            self.champions = other.champions
            self.last_updated = other.last_updated


@dataclass
class ResponseTime:
    """Class representing the Gankster average response time in seconds"""
    time: int = 0

    def formatted_time(self):
        if self.time < 30:
            return "Seconds"
        if self.time < 75:
            return "A Minute"
        if self.time < 300:
            return "A Few Minutes"
        if self.time < 2700:
            return "Many Minutes"
        if self.time < 5040:
            return "An Hours"
        if self.time < 8280:
            return "Two Hours"
        if self.time < 16000:
            return "A Few Hours"
        if self.time < 60000:
            return "Many Hours"
        if self.time < 112320:
            return "A Day"
        if self.time < 190080:
            return "Two Days"
        return "Too Many Days"

@dataclass
class Reputation:
    """Class representing the Gankster reputation"""
    gank_rep: float = 0
    likes: int = 0
    dislikes: int = 0
    response_time: ResponseTime = None
    response_rate: float = 0
    cancellation_rate: float = 0
    communication: float = 0
    behavior: float = 0
    on_time: float = 0
    reviews: list[str] = ()

class GanksterRank(Enum):
    """Enum representing the different possible Gankster ranks"""
    UNRANKED = ("Unranked", 0)
    IRON = ("Iron", 10)
    IRON_BRONZE = ("Iron/Bronze", 15)
    BRONZE = ("Bronze", 20)
    BRONZE_SILVER = ("Bronze/Silver", 25)
    SILVER = ("Silver", 30)
    SILVER_GOLD = ("Silver/Gold", 35)
    GOLD = ("Gold", 40)
    GOLD_PLATINUM = ("Gold/Platinum", 45)
    PLATINUM = ("Platinum", 50)
    PLATINUM_EMERALD = ("Platinum/Emerald", 55)
    EMERALD = ("Emerald", 60)
    EMERALD_DIAMOND = ("Emerald/Diamond", 65)
    DIAMOND = ("Diamond", 70)
    DIAMOND_MASTER = ("Diamond/Master", 75)
    MASTER = ("Master", 80)
    MASTER_GRANDMASTER = ("Master/Grandmaster", 85)
    GRANDMASTER = ("Grandmaster", 90)
    GRANDMASTER_CHALLENGER = ("Grandmaster/Challenger", 95)
    CHALLENGER = ("Challenger", 100)

    def __init__(self, rank: str, gankster_rank: int):
        self.rank = rank
        self.gankster_rank = gankster_rank

    @staticmethod
    def from_gankster_rank(gankster_rank: str):
        for gr in GanksterRank:
            if gr.gankster_rank == gankster_rank:
                return gr


@dataclass
class Team:
    """Class representing a gankster team"""
    number: int = 0
    name: str = ""
    rank: GanksterRank = None
    region: str = ""
    bio: str = ""
    roster: list[Player] = ()
    opggLink: str = ""
    created: datetime = None
    reputation: Reputation = None
    logo_url: str = ""

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

    def copy(self, other):
        if isinstance(other, Team):
            self.number = other.number
            self.name = other.name
            self.rank = other.rank
            self.region = other.region
            self.bio = other.bio
            self.roster = other.roster
            self.opggLink = other.opggLink
            self.created = other.created
            self.reputation = other.reputation
            self.logo_url = other.logo_url

@dataclass
class Scrim:
    """Class representing a Gankster scrim"""
    time: datetime
    scrim_format: ScrimFormat = ScrimFormat.NONE
    team: Team = None
    open: bool = True
    gankster_id: int = 0

    def __eq__(self, other):
        if isinstance(other, Scrim):
            return self.time == other.time and self.scrim_format == other.scrim_format
        return False

    def equals_exact(self, other):
        if isinstance(other, Scrim):
            return self.time == other.time and self.scrim_format == other.scrim_format and self.team == other.team and self.open == other.open
        return False

    def __hash__(self):
        return hash((self.time, self.scrim_format))

    def __str__(self):
        return f"<Scrim: time='{self.time.strftime('%m/%d/%y %I:%M %p')}', format='{self.scrim_format.format_short}', team={str(self.team)}, open={self.open}>"

    def __repr__(self):
        return f"<Scrim: time='{self.time.strftime('%m/%d/%y %I:%M %p')}', format='{self.scrim_format.format_short}', team={self.team}, open={self.open}>"

    def get_scrim_end_time(self) -> datetime:
        return self.time + timedelta(hours=self.scrim_format.games)

    def get_gankster_removal_time(self) -> datetime:
        return self.time + timedelta(minutes=(40 * self.scrim_format.games))

    def get_scrim_start_time_unix(self) -> int:
        return int(self.time.timestamp() * 1000)

    def get_scrim_end_time_unix(self) -> int:
        return int(self.get_scrim_end_time().timestamp() * 1000)

    @staticmethod
    def timestamp_to_datetime(timestamp: int):
        return datetime.fromtimestamp(timestamp / 1000)

class ErrorName(Enum):
    """Enum representing each possible CryoBarkError"""
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
    GANKSTER_NO_CONTENT = "GanksterNoContent"
    GANKSTER_BAD_REQUEST = "GanksterBadRequest"
    GANKSTER_UNAUTHORIZED = "GanksterUnauthorized"
    GANKSTER_FORBIDDEN = "GanksterForbidden"
    GANKSTER_ENDPOINT = "GanksterEndpoint"
    GANKSTER_TIMEOUT = "GanksterTimeout"
    GANKSTER_TOO_MANY_REQUESTS = "GanksterTooManyRequests"
    GANKSTER_DOWN = "GanksterDown"
    GANKSTER_FAILED = "GanksterFailed"
    INVALID_TEAM = "InvalidTeam"
    INVALID_PLAYER = "InvalidPlayer"
    TEAM_NOT_FOUND = "TeamNotFound"

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
    ErrorName.GANKSTER_NO_CONTENT: "No Content was found for the given url or bearer was missing (Gankster 204: No Content)",
    ErrorName.GANKSTER_BAD_REQUEST: "Request format was invalid (Gankster 400: Bad Request)",
    ErrorName.GANKSTER_UNAUTHORIZED: "Authorization was invalid or expired (Gankster 401: Unauthorized)",
    ErrorName.GANKSTER_FORBIDDEN: "The given action was forbidden but authorization was successful (Gankster 403: Forbidden)",
    ErrorName.GANKSTER_ENDPOINT: "The endpoint for the url was not found (Gankster 404: Not Found)",
    ErrorName.GANKSTER_TIMEOUT: "Request took too long to process (Gankster 408: Request Timeout)",
    ErrorName.GANKSTER_TOO_MANY_REQUESTS: "Too many requests have been performed in quick succession (Gankster 429: Too Many Requests)",
    ErrorName.GANKSTER_DOWN: "Gankster is down at the moment (Gankster 500ish)",
    ErrorName.GANKSTER_FAILED: "The given function's success condition failed to be met",
    ErrorName.INVALID_TEAM: "The team stats could not be found for the given team, number or name required",
    ErrorName.INVALID_PLAYER: "The player stats could not be found for the given player, puuid required",
    ErrorName.TEAM_NOT_FOUND: "No team was found with the given name after searching gankster"
}

@dataclass
class CryoBotError(Exception):
    """Class representing a custom error that will be thrown when problem is known"""
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