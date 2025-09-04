from scrim_classes import Scrim, Team, Player
from gankster_api import GanksterAPI
from browser import Browser
from scrim_classes import Scrim, Team

class Gankster:
    def __init__(self):
        self._gankster_api = GanksterAPI()
        self._browser = Browser()

    def retrieve_outgoing_scrims(self, team: Team) -> list[Scrim]:
        """
        Retrieves a list of scrim requests the team has sent out

        Args:
            team (Team): The team to view outgoing scrims for

        Returns:
            list[Scrim]: The list of outgoing scrim requests, team unknown
        """
        # scrims = []
        # for _ in range(int(input("Scrims: "))):
        #     number = input("Number: ")
        #     name = input("Name: ")
        #     # rank = input("Rank: ")
        #     format = ScrimFormat.from_short(input("Format: "))
        #     time = datetime.strptime(input("Datetime (2025-09-03 14:30:00): "), "%Y-%m-%d %H:%M:%S")
        #     team = Team(number=number, name=name)
        #     open = not (name or number)
        #     scrims.append(Scrim(time=time, scrim_format=format, team=team, open=open))
        # return scrims
        return []

    def retrieve_incoming_scrim_requests(self) -> list[Scrim]:
        """
        Retrieves a list of incoming scrim requests to the default user
        Resource Intensive

        Returns:
            list[Scrim]: The list of incoming scrim requests with filled in team
        """
        return self._browser.retrieve_scrim_requests()

    def retrieve_team_number(self, team_name: str) -> str:
        """
        Retrieves the team's number from their name

        Args:
            team (Team): the team class to fill in with the new stats

        Returns:
            None
        """
        return self._browser.retrieve_team_number(team_name)

    def fill_team_stats(self, team: Team) -> None:
        """
        Fills in the stats for the given team based on team number

        Args:
            team (Team): the team class to fill in with the new stats

        Returns:
            None
        """
        return

    def fill_player_stats(self, player: Player) -> None:
        """
        Fills in the stats for the given player based on puuid

        Args:
        player (Player): the player class to fill in with the new stats

        Returns:
            None
        """
        return

    def process_scrim_request(self, scrim: Scrim, accept:bool=True) -> bool:
        """
        Accepts/Declines the given scrim request

        Args:
            scrim (Scrim): The scrim request to accept
            accept (bool): Whether or not to accept the request

        Returns:
            bool: Whether or not the given scrim was found
        """
        return self._browser.process_scrim_request(scrim, accept)

    def create_scrim_request(self, scrim: Scrim) -> None:
        """
        Creates a scrim request

        Args:
            scrim (Scrim): The scrim request to create
        """
        self._browser.create_scrim_request(scrim)

    def cancel_scrim_request(self, scrim: Scrim) -> None:
        """
        Cancels an outgoing scrim request

        Args:
            scrim (Scrim): The scrim request to cancel
        """
        self._browser.cancel_scrim_request(scrim)

    def cancel_all_scrim_requests(self) -> None:
        """
        Cancels all outgoing scrim requests
        """
        self._browser.cancel_scrim_request()

    def send_scrim_request(self, scrim: Scrim) -> None:
        """
        Sends a scrim request

        Args:
            scrim (Scrim): The scrim request to cancel
        """
        self._browser.send_scrim_request(scrim)
