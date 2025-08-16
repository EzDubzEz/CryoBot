import os
import requests
from urllib.parse import urlencode

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

param = {'api_key' : RIOT_API_KEY}

def _errorHandle(url, params):
    rtn = requests.get(url, params=urlencode(params)).json()
    if type(rtn) == dict and  'status' in rtn.keys():
        if rtn['status']['status_code'] == 429 or rtn['status']['status_code'] == 503 or rtn['status']['status_code'] == 503:
            return _errorHandle(url, params)
        else:
            print("ERROR: ", rtn['status']['status_code'])
            # raise Exception("ERRRORR: ", rtn['status']['status_code'])
    return rtn

# AccountDTO
def getAccount(gameName, tagline):
    '''AccountDTO'''
    url = f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagline}'
    params = param.copy()
    return _errorHandle(url, params)

# SummonerDTO
def getSummoner(summonerId):
    '''SummonerDTO'''
    url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/{summonerId}'
    params = param.copy()
    return _errorHandle(url, params)

# List[Entry]
def getGameEntries(puuid, queue=None, count=20, start=0):
    '''List[Entry]'''
    url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'
    params = param.copy()
    params['queue'] = queue
    params['count'] = count
    params['start'] = start
    return _errorHandle(url, params)

# Entry
def getLatestEntry(puuid, queue):
    '''Entry'''
    url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'
    params = param.copy()
    params['queue'] = queue
    params['count'] = 1
    params['start'] = 0
    rtn = _errorHandle(url, params)
    if len(rtn):
        return rtn[0]
    return None

# MatchDTO
def getMatch(matchId):
    '''MatchDTO'''
    url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{matchId}'
    params = param.copy()
    return _errorHandle(url, params)

# Set(LeagueEntryDTO)
def getLeagueEntries(puuid):
    '''Set(LeagueEntryDTO)'''
    url = f'https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}'
    params = param.copy()
    return _errorHandle(url, params)

# (Tier, Rank, LP)
def getRank(puuid, queue):
    '''(Tier, Rank, LP)'''
    for entry in getLeagueEntries(puuid):
        if entry["queueType"] == queue:
            return (entry["tier"], entry["rank"], entry["leaguePoints"])
    return None
