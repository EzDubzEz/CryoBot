import asyncio

from browser import Browser
from gankster_api import GanksterAPI
from helper import getVariable
from scrim_classes import Player, Scrim, Team

CRYOBARK: Team = getVariable("CRYOBARK")
WILDCARD_TEAM: Team = getVariable("WILDCARD_TEAM")

class Gankster:
    """
    Handles everything to do with Gankster and determines best sub class to perform task

    Currently just a passthrough since Browser is deprecated and GanksterAPI does everything
    """
    def __init__(self):
        self._gankster_api = GanksterAPI()
        # self._browser = Browser()

    async def refresh(self):
        """
        Refreshes everything for gankster to be called every so often

        Returns:
            None
        """
        await asyncio.to_thread(self._gankster_api.refresh_bearer)

    async def retrieve_outgoing_scrims(self, team: Team) -> list[Scrim]:
        """
        Retrieves a list of scrim requests the team has sent out

        Args:
            team (Team): The team to view outgoing scrims for

        Returns:
            list[Scrim]: The list of outgoing scrim requests, team unknown

        Raises:
            CryoBotError: If issue occurs
        """
        return await asyncio.to_thread(self._gankster_api.retrieve_outgoing_scrims, team)

    async def retrieve_incoming_scrim_requests(self) -> list[Scrim]:
        """
        Retrieves a list of incoming scrim requests to the default user

        Returns:
            list[Scrim]: The list of incoming scrim requests with filled in team

        Raises:
            CryoBotError: If issue occurs
        """
        return await asyncio.to_thread(self._gankster_api.retrieve_incoming_scrim_requests)

    async def retrieve_outgoing_scrim_requests(self) -> list[Scrim]:
        """
        Retrieves a list of outgoing scrim requests to the default user

        Returns:
            list[Scrim]: The list of outgoing scrim requests with filled in team

        Raises:
            CryoBotError: If issue occurs
        """
        return await asyncio.to_thread(self._gankster_api.retrieve_outgoing_scrim_requests)

    async def fill_team_stats(self, team: Team) -> None:
        """
        Fills in the stats for the given team based on team number

        Args:
            team (Team): the team class to fill in with the new stats

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """
        await asyncio.to_thread(self._gankster_api.fill_team_stats, team)

    async def update_team_players(self, team: Team) -> None:
        """
        Fills in the stats for the given team and updatees players

        Args:
            team (Team): the team class to fill in with the new stats and update players for

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """
        await asyncio.to_thread(self._gankster_api.update_team_players, team)

    async def fill_player_stats(self, player: Player) -> None:
        """
        Fills in the stats for the given player based on puuid

        Args:
        player (Player): the player class to fill in with the new stats

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """
        await asyncio.to_thread(self._gankster_api.fill_player_stats, player)

    async def process_scrim_request(self, scrim: Scrim, accept:bool=True) -> bool:
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
        return await asyncio.to_thread(self._gankster_api.process_scrim_request, scrim, accept)

    async def create_scrim_request(self, scrim: Scrim) -> None:
        """
        Creates a scrim request

        Args:
            scrim (Scrim): The scrim request to create

        Raises:
            CryoBotError: If issue occurs
        """
        await asyncio.to_thread(self._gankster_api.create_scrim_request, scrim)

    async def cancel_scrim_request(self, scrim: Scrim) -> None:
        """
        Cancels an outgoing scrim request

        Args:
            scrim (Scrim): The scrim request to cancel

        Raises:
            CryoBotError: If issue occurs
        """
        await asyncio.to_thread(self._gankster_api.cancel_scrim_request, scrim)

    async def cancel_scrim_block(self, scrim: Scrim, message: str) -> None:
        """
        Cancels a confirmed scrim block

        Args:
            scrim (Scrim): The scrim block to cancel

        Raises:
            CryoBotError: If issue occurs
        """
        await asyncio.to_thread(self._gankster_api.cancel_scrim_block, scrim, message)

    async def send_scrim_request(self, scrim: Scrim) -> None:
        """
        Sends a scrim request

        Args:
            scrim (Scrim): The scrim request to cancel

        Raises:
            CryoBotError: If issue occurs
        """
        await asyncio.to_thread(self._gankster_api.send_scrim_request, scrim)