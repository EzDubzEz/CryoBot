import requests
from urllib.parse import urlencode
from helper import getVariable
from time import sleep

RIOT_API_KEY: str = getVariable("RIOT_API_KEY")

class RiotAPI:
    param = {'api_key' : RIOT_API_KEY}

    @staticmethod
    def get(url, params, attempts=0):
        rtn = requests.get(url, params=urlencode(params)).json()
        if type(rtn) == dict and  'status' in rtn.keys():
            retryCodes = [
                429, # Rate Limit Exceeded
                500, # Internal Server Error
                503, # Service Unavailable
            ]
            if rtn['status']['status_code'] in retryCodes and attempts < 120:
                sleep(.25)
                return RiotAPI.get(url, params, attempts+1)
            else:
                print("ERROR: ", rtn['status']['status_code'])
                # raise Exception("ERRRORR: ", rtn['status']['status_code'])
        return rtn

    # AccountDTO
    @staticmethod
    def getAccount(self, gameName, tagline):
        '''AccountDTO'''
        url = f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagline}'
        params = RiotAPI.param.copy()
        return RiotAPI.get(url, params)

    # SummonerDTO
    @staticmethod
    def getSummoner(self, summonerId):
        '''SummonerDTO'''
        url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/{summonerId}'
        params = RiotAPI.param.copy()
        return RiotAPI.get(url, params)

    # List[Entry]
    @staticmethod
    def getGameEntries(puuid, queue=None, count=20, start=0):
        '''List[Entry]'''
        url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'
        params = RiotAPI.param.copy()
        params['queue'] = queue
        params['count'] = count
        params['start'] = start
        return RiotAPI.get(url, params)

    # Entry
    @staticmethod
    def getLatestEntry(puuid, queue):
        '''Entry'''
        url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'
        params = RiotAPI.param.copy()
        params['queue'] = queue
        params['count'] = 1
        params['start'] = 0
        rtn = RiotAPI.get(url, params)
        if len(rtn):
            return rtn[0]
        return None

    # MatchDTO
    @staticmethod
    def getMatch(matchId):
        '''MatchDTO'''
        url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{matchId}'
        params = RiotAPI.param.copy()
        return RiotAPI.get(url, params)

    # Set(LeagueEntryDTO)
    @staticmethod
    def getLeagueEntries(puuid):
        '''Set(LeagueEntryDTO)'''
        url = f'https://na1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}'
        params = RiotAPI.param.copy()
        return RiotAPI.get(url, params)

    # (Tier, Rank, LP)
    @staticmethod
    def getRank(puuid, queue):
        '''(Tier, Rank, LP)'''
        for entry in RiotAPI.getLeagueEntries(puuid):
            if entry["queueType"] == queue:
                return (entry["tier"], entry["rank"], entry["leaguePoints"])
        return None