from datetime import datetime
from enum import Enum
from dataclasses import dataclass

class ScrimFormat(Enum):
    BEST_OF_ONE = "Bo1"
    BEST_OF_TWO = "Bo2"
    BEST_OF_THREE = "Bo3"
    BEST_OF_FOUR = "Bo4"
    BEST_OF_FIVE = "Bo5"
    ONE_GAME = "1 Game"
    TWO_GAMES = "2 Games"
    THREE_GAMES = "3 Games"
    FOUR_GAMES = "4 Games"
    FIVE_GAMES = "5 Games"

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
    champions: list[str] = []

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
    reviews: list[str] = []

@dataclass
class Team:
    """Class representing a gankster team"""
    number: str
    name: str
    rank: str = "" #Team ranks are different than individual rank
    region: str = ""
    bio: str = ""
    roster: list[Player] = []
    subs: list[Player] = []
    opggLink: str = ""
    created: datetime = None
    reputation: Reputation

@dataclass
class Scrim:
    time: datetime
    scrimFormat: ScrimFormat
    team: Team = None
    open: bool = True