import requests
from datetime import datetime, timedelta
from time import sleep

from helper import getVariable, setVariable, debugPrint
from scrim_classes import Scrim, Team, Player, Champion, ScrimFormat, GanksterRank, ResponseTime, Reputation, CryoBotError, ErrorName

GANKSTER_API_KEY: str = getVariable("GANKSTER_API_KEY")
CRYOBARK: Team = getVariable("CRYOBARK")

class GanksterAPI:
    def __init__(self):
        self._bearer: str = ""
        self._headers: dict[str, str] = {"authorization": self._bearer, "cookie": f"g-active-team={CRYOBARK.number}"}
        self._refresh_token: str = getVariable("GANKSTER_REFRESH_TOKEN")

        self.refresh_bearer()
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
    def refresh_bearer(self):
        url = f"https://securetoken.googleapis.com/v1/token?key={GANKSTER_API_KEY}"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
        }

        resp = requests.post(url, data=payload)
        resp.raise_for_status()
        data = resp.json()
        self._bearer = f"Bearer {data['access_token']}"
        self._headers["authorization"] = self._bearer
        self._headers["authorization"] = self._headers["authorization"]
        self._refresh_token = data["refresh_token"]
        setVariable("GANKSTER_REFRESH_TOKEN", self._refresh_token)

    def _handle_response(self, response: requests.Response, error_fields: str) -> dict:
        """
        Parses response and raises error if request was invalid

        Args:
            response (requests.Response): The response to parse
            error_fields (str): The error fields to return if an error occured

        Returns:
            response (dict): The jsonified response if all was successful

        Raises:
            CryoBotError: If issue occurs
        """
        if response.status_code == 200 or response.status_code == 201:
            try: return response.json()
            except: return None
        if response.status_code == 204:
            raise CryoBotError(ErrorName.GANKSTER_NO_CONTENT, error_fields)
        if response.status_code == 400:
            raise CryoBotError(ErrorName.GANKSTER_BAD_REQUEST, error_fields)
        if response.status_code == 401:
            raise CryoBotError(ErrorName.GANKSTER_UNAUTHORIZED, error_fields)
        if response.status_code == 403:
            raise CryoBotError(ErrorName.GANKSTER_FORBIDDEN, error_fields)
        if response.status_code == 404:
            raise CryoBotError(ErrorName.GANKSTER_ENDPOINT, error_fields)
        if response.status_code == 408:
            raise CryoBotError(ErrorName.GANKSTER_TIMEOUT, error_fields)
        if response.status_code == 429:
            raise CryoBotError(ErrorName.GANKSTER_TOO_MANY_REQUESTS, error_fields)
        if response.status_code >= 500 and response.status_code <=504:
            raise CryoBotError(ErrorName.GANKSTER_UNAVAILIBLE, error_fields + f", status_code={response.status_code}")
        raise CryoBotError(ErrorName.GANKSTER_FAILED, error_fields + f", status_code={response.status_code}")

    def _make_call(self, type: str, url: str, payload: list[dict]=[]) -> dict:
        """
        Makes a request call and handles the response

        Args:
            type (str): the type of request to make (GET, POST, etc.)
            url (str): The url to make the request
            payload (list[dict]): the payload for the request if needed

        Returns:
            response (dict): The jsonified response

        Raises:
            CryoBotError: If issue occurs
        """
        if type == "GET":
            response = requests.get(url, headers=self._headers)
            return self._handle_response(response, f"type='GET', url='{url}'")
        if type == "DELETE":
            response = requests.delete(url, headers=self._headers)
            return self._handle_response(response, f"type='DELETE', url='{url}'")
        if type == "POST":
            response = requests.post(url, headers=self._headers, json=payload)
            return self._handle_response(response, f"type='POST', url='{url}', payload={payload}")
        if type == "PATCH":
            response = requests.patch(url, headers=self._headers, json=payload)
            return self._handle_response(response, f"type='PATCH', url='{url}', payload={payload}")

    def _retrieve_outgoing_public_scrims(self, team: Team) -> list[Scrim]:
        if not team.number:
            if not team.name:
                team = CRYOBARK
            else:
                team.number = self._retrieve_team_number(team.name)

        url = f"https://lol.gankster.gg/api/v1/events/public/{team.number}" #TestingT (107750)  Rndm (112630)
        response = self._make_call("GET", url)

        scrims = []

        for scrim in response["lfsEvents"]:
            if scrim["status"] == "OPEN":
                scrims.append(Scrim(Scrim.timestamp_to_datetime(scrim["startTime"]), ScrimFormat.from_gankster_format(scrim["format"]["bestOf"]), gankster_id=scrim["id"]))
            if scrim["status"] == "BOOKED" and (team != CRYOBARK):
                scrims.append(Scrim(Scrim.timestamp_to_datetime(scrim["startTime"]), ScrimFormat.from_gankster_format(scrim["format"]["bestOf"]), open=False, gankster_id=scrim["id"]))

        return scrims

    def retrieve_booked_scrims(self) -> list[Scrim]:
        url = "https://lol.gankster.gg/api/v1/chats/scrim"
        response = self._make_call("GET", url)
   
        scrims = []

        for result in response["results"]:
            if result["type"] == "SCRIM" and result["event"]["status"] == "CONFIRMED" and Scrim.timestamp_to_datetime(result["event"]["endTime"]) > datetime.now():
                if result["event"]["requesterId"] == CRYOBARK.number:
                    team = "teamB"
                else:
                    team = "teamA"
                scrims.append(Scrim(Scrim.timestamp_to_datetime(result["event"]["startTime"]), ScrimFormat.from_gankster_format(result["event"]["format"]["bestOf"]),
                                    team=self._parse_team(result["event"][team]["team"]), open=False, gankster_id=result["event"]["id"]))

        return scrims

    def retrieve_outgoing_scrims(self, team: Team) -> list[Scrim]:
        scrims = self._retrieve_outgoing_public_scrims(team)

        if team != CRYOBARK:
            return scrims

        return scrims + self.retrieve_booked_scrims()

    def retrieve_incoming_scrim_requests(self) -> list[Scrim]:
        url = "https://lol.gankster.gg/api/v1/chats/scrim"
        response = self._make_call("GET", url)

        scrims = []
        for result in response["results"]:
            if (result["type"] == "SCRIM" and result["event"]["status"] == "REQUESTED" and result["event"]["requesterId"] != CRYOBARK.number
                and Scrim.timestamp_to_datetime(result["event"]["endTime"]) > datetime.now()):
                scrims.append(Scrim(Scrim.timestamp_to_datetime(result["event"]["startTime"]), ScrimFormat.from_gankster_format(result["event"]["format"]["bestOf"]),
                                    team=self._parse_team(result["event"]["teamA"]["team"]), open=True, gankster_id=result["event"]["id"]))

        return scrims

    def retrieve_outgoing_scrim_requests(self) -> list[Scrim]:
        url = "https://lol.gankster.gg/api/v1/chats/scrim"
        response = self._make_call("GET", url)

        scrims = []
        for result in response["results"]:
            if (result["type"] == "SCRIM" and result["event"]["status"] == "REQUESTED" and result["event"]["requesterId"] == CRYOBARK.number
                and Scrim.timestamp_to_datetime(result["event"]["endTime"]) > datetime.now()):
                scrims.append(Scrim(Scrim.timestamp_to_datetime(result["event"]["startTime"]), ScrimFormat.from_gankster_format(result["event"]["format"]["bestOf"]),
                                    team=self._parse_team(result["event"]["teamB"]["team"]), open=True, gankster_id=result["event"]["id"]))

        return scrims

    def fill_team_stats(self, team: Team) -> None:
        if team.number:
            url = f"https://lol.gankster.gg/api/v1/teams/{team.number}"
            response = self._make_call("GET", url)

            team.copy(self._parse_team(response))
        elif team.name:
            url = f"https://lol.gankster.gg/api/v1/teams/search_advanced?query={team.name}"
            response = self._make_call("GET", url)

            if not len(response["results"]):
                raise CryoBotError(ErrorName.TEAM_NOT_FOUND, f"team={team}")

            team.copy(self._parse_team(response["results"][0]["team"]))
        else:
            raise CryoBotError(ErrorName.INVALID_TEAM, f"team={team}")

    def _retrieve_team_number(self, team_name) -> None:
            url = f"https://lol.gankster.gg/api/v1/teams/search_advanced?query={team_name}"
            response = self._make_call("GET", url)

            if not len(response["results"]):
                raise CryoBotError(ErrorName.TEAM_NOT_FOUND, f"team_name={team_name}")

            return response["results"][0]["team"]["id"]

    def fill_player_stats(self, player: Player) -> None:
        if not player.puuid:
            raise CryoBotError(ErrorName.INVALID_PLAYER, f"player={player}")
        if not player.server:
            player.server = "NA"

        url = f"https://lol.gankster.gg/api/v1/lol/player/data/stats?puuid={player.puuid}&server={player.server}"
        response = self._make_call("GET", url)

        player.copy(self._parse_player(response["player"]))


    def process_scrim_request(self, scrim: Scrim, accept:bool=True) -> bool:
        scrims = self.retrieve_incoming_scrim_requests()

        found = False
        for i in range(len(scrims)):
            if scrims[i].time == scrim.time and scrims[i].scrim_format == scrim.scrim_format and scrims[i].team.name == scrim.team.name:
                found = True
                break
        if not found:
            raise CryoBotError(ErrorName.NO_SCRIM_BLOCK_FOUND, f"scrim={scrim}")

        url = f"https://lol.gankster.gg/api/v1/events/{scrims[i].gankster_id}" # patch
        if accept:
            payload = {
                "eventType": "SCRIM",
                "startTime": scrims[i].get_scrim_start_time_unix(),
                "endTime": scrims[i].get_scrim_end_time_unix(),
                "format": {"bestOf": scrims[i].scrim_format.gankster_format},
                "status": "CONFIRMED"
            }
        else:
            payload = {
                "eventType": "SCRIM",
                "status": "REJECTED"
            }
        self._make_call("PATCH", url, payload)
        pass

    def create_scrim_request(self, scrim: Scrim) -> None:
        url = "https://lol.gankster.gg/api/v1/events/bulk"
        payload = [{"endTime": scrim.get_scrim_end_time_unix(),
            "eventType": "LFS",
            "format": {"bestOf": scrim.scrim_format.gankster_format},
            "isHighlighted": False,
            "isNow": False,
            "isPublic": True,
            "startTime": scrim.get_scrim_start_time_unix()}]
        self._make_call("POST", url, payload)

    def cancel_scrim_request(self, scrim: Scrim) -> None:
        scrims = self._retrieve_outgoing_public_scrims(CRYOBARK)

        found = False
        for i in range(len(scrims)):
            if scrims[i].time == scrim.time:
                found = True
                break
        if not found:
            raise CryoBotError(ErrorName.NO_SCRIM_BLOCK_FOUND, f"scrim={scrim}")

        url = f"https://lol.gankster.gg/api/v1/events/{scrims[i].gankster_id}"
        self._make_call("DELETE", url)

    def cancel_scrim_block(self, scrim: Scrim, msg: str) -> None:
        scrims = self.retrieve_booked_scrims()

        found = False
        for i in range(len(scrims)):
            if scrims[i].time == scrim.time and scrims[i].team.name == scrim.team.name:
                found = True
                break
        if not found:
            raise CryoBotError(ErrorName.NO_SCRIM_BLOCK_FOUND, f"scrim={scrim}")

        url = f"https://lol.gankster.gg/api/v1/events/{scrims[i].gankster_id}"
        payload = {
            "cancellationReason": msg,
            "eventType": "SCRIM",
            "status": "CANCELED"
        }

        self._make_call("PATCH", url, payload)

    def send_scrim_request(self, scrim: Scrim) -> None:
        if not scrim.team.number:
            if scrim.team.name:
                scrim.team.number = self._retrieve_team_number(scrim.team.name)
            else:
                raise CryoBotError(ErrorName.INVALID_TEAM, f"team={scrim.team}")

        scrim_requests = self._retrieve_outgoing_public_scrims(scrim.team)
        lfs_id = ""
        for scrim_request in scrim_requests:
            if scrim_request.open:
                lfs_id = scrim_request.gankster_id
                break
        if not lfs_id:
            raise CryoBotError(ErrorName.NO_TEAM_OUTGOING_SCRIM_REQUEST, fields=f"scrim={scrim}")

        url = "https://lol.gankster.gg/api/v1/events"
        payload = {
            "endTime": scrim.get_scrim_end_time_unix(),
            "eventType": "SCRIM",
            "format": {"bestOf": scrim.scrim_format.gankster_format},
            "lfsId": lfs_id,
            "opponentId": scrim.team.number,
            "startTime": scrim.get_scrim_start_time_unix()
        }

        self._make_call("POST", url, payload)
        pass

    def update_team_players(self, team: Team) -> None:
        self.fill_team_stats(team)
        for player in team.roster:
            if player.last_updated < datetime.now() - timedelta(hours=24):
                try: self._update_player(player)
                except CryoBotError as e: debugPrint(f"Failed to update player: {player.name}")

    def _update_player(self, player: Player) -> None:
        if not player.puuid:
            raise CryoBotError(ErrorName.INVALID_PLAYER, f"player={player}")
        if not player.server:
            player.server = "NA"

        url = "https://lol.gankster.gg/api/v1/lol/player/data/stats"
        payload = {
            "puuid": player.puuid,
            "server": player.server
        }
        response = self._make_call("PATCH", url, payload)
        player.copy(response["player"])

    def _parse_team(self, team: dict) -> Team:
        return Team(number=team["id"], name=team["name"], rank=GanksterRank.from_gankster_rank(team["lolRank"]), region=team["lolServer"], bio=team.get("bio") or "",
             roster=self._parse_players(team["lolRoster"]), opggLink=team.get("opggLink", "") or "", created=Scrim.timestamp_to_datetime(team["createdAt"]),
             reputation=self._parse_reputation(team["reputation"]), logo_url=team.get("logo") or "")

    def _parse_players(self, players: list[dict]) -> list[Player]:
        [Player(name=player["playerData"]["name"], rank=f'{GanksterRank.from_gankster_rank(player["playerData"]["rank"]).rank} {player["playerData"]["division"]}',
                tag=player["playerData"]["tag"], puuid=player["playerData"]["puuid"], server=player["playerData"]["server"],
                champions= [] if "stats" not in player["playerData"] else self._parse_champions(player["playerData"]["stats"]["champions"]), is_sub=player["isSub"],
                last_updated=datetime.now() if "stats" not in player["playerData"] else Scrim.timestamp_to_datetime(player["playerData"]["stats"]["updatedAt"])) for player in players]

    def _parse_player(self, player: dict) -> Player:
        return Player(name=player["name"], rank=f'{GanksterRank.from_gankster_rank(player["rank"]).rank} {player["division"]}', tag=player["tag"], puuid=player["puuid"],
                      server=player["server"], champions=self._parse_champions(player["stats"]["champions"]), last_updated=Scrim.timestamp_to_datetime(player["stats"]["updatedAt"]))

    def _parse_champions(self, champions: list[dict]) -> list[Champion]:
        return [Champion(name=champ["name"], level=champ["level"], points=champ["points"], image_url=champ['imageURL']) for champ in champions]

    def _parse_reputation(self, reputation: dict) -> Reputation:
        return Reputation(gank_rep=reputation["rating"], likes=reputation["posTotalCount"], dislikes=reputation["negTotalCount"], response_time=ResponseTime(reputation["responseTimeSec"]),
                          cancellation_rate=reputation["cancellationRate"], response_rate=reputation["responseRate"], communication=reputation["feedbackCommunicationScore"], behavior=reputation["feedbackBehaviorScore"],
                          on_time=reputation["feedbackOnTimeScore"])

# if __name__ == "__main__":
    # scrims = GanksterAPI().retrieve_outgoing_scrims(CRYOBARK)
    # # print(scrims)
    # player = Player("", "", puuid="uZGaTQBfV9GW9IjKoJRcMY0CoKUQ82Vlb8536qGzLck1xFKpzlaUwPq5609L8WHZUGphR2Y7ro6dHg", server="NA")
    # gank = GanksterAPI()
    # scrim = Scrim(datetime.strptime('10/07/25 10:00', '%m/%d/%y %H:%M'), ScrimFormat.FOUR_GAMES, Team(name="TeamTrebo"))
    # skrim = Scrim(datetime.strptime('09/29/25 10:00', '%m/%d/%y %H:%M'), ScrimFormat.FOUR_GAMES, Team(name="TeamTrebo", number=111773))
    # import time
    # start = time.time()
    # # gank.update_team_players(Team(89033))
    # # gank.create_scrim_request(scrim)
    # # gank.cancel_scrim_block(scrim, "scrim canceled")
    # # gank.process_scrim_request(scrim, False)
    # gank.send_scrim_request(scrim)
    # # gank.cancel_scrim_request(scrim)
    # # GanksterAPI().update_player(player)
    # # GanksterAPI().fill_player_stats(player)
    # # GanksterAPI().fill_team_stats(CRYOBARK)
    # # print(gank.retrieve_incoming_scrim_requests())
    # # print(gank.retrieve_outgoing_scrim_requests())
    # print(time.time() - start)
    # print()
    # print()