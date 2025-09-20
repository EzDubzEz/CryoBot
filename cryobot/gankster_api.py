
from datetime import datetime, timedelta

import requests

from helper import debugPrint, getVariable, setVariable
from scrim_classes import Champion, CryoBotError, ErrorName, GanksterRank, Player, Reputation, ResponseTime, Scrim, ScrimFormat, Team

GANKSTER_API_KEY: str = getVariable("GANKSTER_API_KEY")
CRYOBARK: Team = getVariable("CRYOBARK")

class GanksterAPI:
    """
    Handles everything that has to do with gankster API calls, and everything currently supports everything that uses gankster

    GANKSTER_REFRESH_TOKEN (in update_vars.json) needed
    """
    def __init__(self):
        self._bearer: str = ""
        self._headers: dict[str, str] = {"authorization": self._bearer, "cookie": f"g-active-team={CRYOBARK.number}"}
        self._refresh_token: str = getVariable("GANKSTER_REFRESH_TOKEN")

        self.refresh_bearer()

    def refresh_bearer(self) -> None:
        """
        Refreshes everything for gankster to be called every so often

        Returns:
            None
        """
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
        """
        Retrieves a list of scrim requests the team has sent out visible to the public (open/booked)
        If the team is Cryobark it will ignore booked scrims

        Args:
            team (Team): The team to view outgoing public scrims for

        Returns:
            list[Scrim]: The list of outgoing public scrim requests, team unknown

        Raises:
            CryoBotError: If issue occurs
        """
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
            if scrim["status"] == "BOOKED":
                scrims.append(Scrim(Scrim.timestamp_to_datetime(scrim["startTime"]), ScrimFormat.from_gankster_format(scrim["format"]["bestOf"]), open=False, gankster_id=scrim["id"]))

        return scrims

    def retrieve_booked_scrims(self) -> list[Scrim]:
        """
        Retrieves a list of Cryobark's booked scrims

        Returns:
            list[Scrim]: The list of booked scrims

        Raises:
            CryoBotError: If issue occurs
        """
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
        """
        Retrieves a list of scrim requests the team has sent out

        Args:
            team (Team): The team to view outgoing scrims for

        Returns:
            list[Scrim]: The list of outgoing scrim requests, team unknown if not for Cryobark

        Raises:
            CryoBotError: If issue occurs
        """
        public_scrims = self._retrieve_outgoing_public_scrims(team)

        if team != CRYOBARK:
            return public_scrims

        booked_scrims = self.retrieve_booked_scrims()

        for public_scrim in public_scrims:
            if not public_scrim.open:
                if public_scrim in booked_scrims:
                    public_scrim.team = booked_scrims[booked_scrims.index(public_scrim)].team
                    booked_scrims.remove(public_scrim)

        return public_scrims

    def retrieve_incoming_scrim_requests(self) -> list[Scrim]:
        """
        Retrieves a list of incoming scrim requests for Cryobark

        Returns:
            list[Scrim]: The list of incoming scrim requests with filled in team

        Raises:
            CryoBotError: If issue occurs
        """
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
        """
        Retrieves a list of outgoing scrim requests from Cryobark

        Returns:
            list[Scrim]: The list of outgoing scrim requests with filled in team

        Raises:
            CryoBotError: If issue occurs
        """
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
        """
        Fills in the stats for the given team based on team number

        Args:
            team (Team): the team class to fill in with the new stats

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """
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

    def _retrieve_team_number(self, team_name) -> int:
        """
        Retrieves the team number from the given team name

        Args:
        team_name (str): the team's name to search for

        Returns:
            int: the team's team number

        Raises:
            CryoBotError: If issue occurs
        """
        url = f"https://lol.gankster.gg/api/v1/teams/search_advanced?query={team_name}"
        response = self._make_call("GET", url)

        if not len(response["results"]):
            raise CryoBotError(ErrorName.TEAM_NOT_FOUND, f"team_name={team_name}")

        return response["results"][0]["team"]["id"]

    def fill_player_stats(self, player: Player) -> None:
        """
        Fills in the stats for the given player based on puuid

        Args:
        player (Player): the player class to fill in with the new stats

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """
        if not player.puuid:
            raise CryoBotError(ErrorName.INVALID_PLAYER, f"player={player}")
        if not player.server:
            player.server = "NA"

        url = f"https://lol.gankster.gg/api/v1/lol/player/data/stats?puuid={player.puuid}&server={player.server}"
        response = self._make_call("GET", url)

        player.copy(self._parse_player(response["player"]))


    def process_scrim_request(self, scrim: Scrim, accept:bool=True) -> bool:
        """
        Accepts/Declines the given scrim request

        Args:
            scrim (Scrim): The scrim request to accept
            accept (bool): Whether or not to accept the request

        Returns:
            bool: Whether or not the given scrim was found

        Raises:
            CryoBotError: If issue occurs
        """
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

    def create_scrim_request(self, scrim: Scrim) -> None:
        """
        Creates a scrim request

        Args:
            scrim (Scrim): The scrim request to create

        Raises:
            CryoBotError: If issue occurs
        """
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
        """
        Cancels an outgoing scrim request

        Args:
            scrim (Scrim): The scrim request to cancel

        Raises:
            CryoBotError: If issue occurs
        """
        scrims = self._retrieve_outgoing_public_scrims(CRYOBARK)

        found = False
        for i in range(len(scrims)):
            if scrims[i].time == scrim.time and scrims[i].open:
                found = True
                break
        if not found:
            raise CryoBotError(ErrorName.NO_SCRIM_BLOCK_FOUND, f"scrim={scrim}")

        url = f"https://lol.gankster.gg/api/v1/events/{scrims[i].gankster_id}"
        self._make_call("DELETE", url)

    def cancel_scrim_block(self, scrim: Scrim, msg: str) -> None:
        """
        Cancels a confirmed scrim block

        Args:
            scrim (Scrim): The scrim block to cancel

        Raises:
            CryoBotError: If issue occurs
        """
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
        """
        Sends a scrim request

        Args:
            scrim (Scrim): The scrim request to cancel

        Raises:
            CryoBotError: If issue occurs
        """
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

    def update_team_players(self, team: Team) -> None:
        """
        Fills in the stats for the given team and updatees players

        Args:
            team (Team): the team class to fill in with the new stats and update players for

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """
        self.fill_team_stats(team)
        for player in team.roster:
            if player.last_updated < datetime.now() - timedelta(hours=24):
                try: self._update_player(player)
                except CryoBotError as e: debugPrint(f"Failed to update player: {player.name}")

    def _update_player(self, player: Player) -> None:
        """Updates the given player on gankster and fills in their new stats"""
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
        """Pareses the retrieved json team and returns value"""
        return Team(number=team["id"], name=team["name"], rank=GanksterRank.from_gankster_rank(team["lolRank"]), region=team["lolServer"], bio=team.get("bio") or "",
             roster=self._parse_players(team["lolRoster"]), opggLink=team.get("opggLink", "") or "", created=Scrim.timestamp_to_datetime(team["createdAt"]),
             reputation=self._parse_reputation(team["reputation"]), logo_url=team.get("logo") or "")

    def _parse_players(self, players: list[dict]) -> list[Player]:
        """Parses the retrieved json players list and returns value"""
        [Player(name=player["playerData"]["name"], rank=f'{GanksterRank.from_gankster_rank(player["playerData"]["rank"]).rank} {player["playerData"]["division"]}',
                tag=player["playerData"]["tag"], puuid=player["playerData"]["puuid"], server=player["playerData"]["server"],
                champions= [] if "stats" not in player["playerData"] else self._parse_champions(player["playerData"]["stats"]["champions"]), is_sub=player["isSub"],
                last_updated=datetime.now() if "stats" not in player["playerData"] else Scrim.timestamp_to_datetime(player["playerData"]["stats"]["updatedAt"])) for player in players]

    def _parse_player(self, player: dict) -> Player:
        """Parses the retrieved json player and returns value"""
        return Player(name=player["name"], rank=f'{GanksterRank.from_gankster_rank(player["rank"]).rank} {player["division"]}', tag=player["tag"], puuid=player["puuid"],
                      server=player["server"], champions=self._parse_champions(player["stats"]["champions"]), last_updated=Scrim.timestamp_to_datetime(player["stats"]["updatedAt"]))

    def _parse_champions(self, champions: list[dict]) -> list[Champion]:
        """Parses the retrieved json champions list and returns value"""
        return [Champion(name=champ["name"], level=champ["level"], points=champ["points"], image_url=champ['imageURL']) for champ in champions]

    def _parse_reputation(self, reputation: dict) -> Reputation:
        """Parses the retrieved json reputation and returns value"""
        return Reputation(gank_rep=reputation["rating"], likes=reputation["posTotalCount"], dislikes=reputation["negTotalCount"], response_time=ResponseTime(reputation["responseTimeSec"]),
                          cancellation_rate=reputation["cancellationRate"], response_rate=reputation["responseRate"], communication=reputation["feedbackCommunicationScore"], behavior=reputation["feedbackBehaviorScore"],
                          on_time=reputation["feedbackOnTimeScore"])