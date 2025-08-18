from scrim_classes import Scrim, Team, Player
from gankster_api import GanksterAPI
from browser import Browser

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
        return

    def retrieve_incoming_scrim_requests(self) -> list[Scrim]:
        """
        Retrieves a list of incoming scrim requests to the default user
        Resource Intensive

        Returns:
            list[Scrim]: The list of incoming scrim requests with filled in team
        """
        return self._browser.retrieve_scrim_requests()

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

    def process_scrim_requests(self, scrim: Scrim, accept:bool=True) -> bool:
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
        Cancels a scrim request

        Args:
            scrim (Scrim): The scrim request to cancel
        """
        self._browser.cancel_scrim_request(scrim)