import os
import pathlib
import subprocess

from aiohttp import ClientSession
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from helper import getVariable
from scrim_classes import CryoBotError, ErrorName, Scrim

GOOGLE_SCOPES: list[str] = getVariable("GOOGLE_SCOPES")
CLIENT_ID: int = getVariable("CLIENT_ID")
CLIENT_SECRET: str = getVariable("CLIENT_SECRET")
GOOGLE_URL: str = getVariable("GOOGLE_URL")

class GoogleAPI:
    def __init__(self):
        self._creds = self._get_creds()

    def _get_creds(self) -> Credentials:
        creds = None
        if os.path.exists('google_auth_token.json'):
            creds = Credentials.from_authorized_user_file('google_auth_token.json', GOOGLE_SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                return None
            with open('google_auth_token.json', 'w') as token_file:
                token_file.write(creds.to_json())
        self._headers = {"Authorization": f"Bearer {creds.token}","Content-Type": "application/json"}
        return creds

    def setup_creds(self) -> None:
        """
        Opens a browser and goes to link to let the user authenticate
        Should be called manually, not by another class

        Returns:
            None
        """
        flow = InstalledAppFlow.from_client_config({
            "installed": {
                "client_id": CLIENT_ID,
                "project_id": "cryobark",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_secret": CLIENT_SECRET
            }
        }, GOOGLE_SCOPES)

        flow.redirect_uri = "http://localhost:8080/"
        auth_url, state = flow.authorization_url(prompt='consent')
        subprocess.Popen([
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "--profile-directory=Default",
            f"--user-data-dir={pathlib.Path().resolve()}/ChromeProfile",
            auth_url
        ])

        self._creds = flow.run_local_server(port=8080, open_browser=False, state=state)
        self._headers = {"Authorization": f"Bearer {self._creds.token}","Content-Type": "application/json"}

        with open('google_auth_token.json', 'w') as token_file:
            token_file.write(self._creds.to_json())

    async def refresh_creds(self)->None:
        """
        Call occasionally to just keep auth going good and creds refreshed

        Returns:
            None
        """
        self._creds.refresh(Request())
        try:
            await self.update_scrim_results()
        except:
            pass

    def is_auth_setup(self) -> bool:
        return self._creds != None

    async def _make_call(self, payload):
        if not self.is_auth_setup():
            raise CryoBotError(ErrorName.AUTH_NOT_SETUP, fields="D:")
        async with ClientSession() as session:
            async with session.post(GOOGLE_URL, headers=self._headers, json=payload) as resp:
                response = await resp.json()

        if "error" in response:
            messages = response["error"]["details"][0]["errorMessage"].removeprefix("Error: ").split(": ")
            if messages[0] in (e.value for e in ErrorName):
                raise CryoBotError(ErrorName(messages[0]), messages[1])
            raise CryoBotError(ErrorName.UNKNOWN, "", description=": ".join(messages))

    async def found_scrim(self, scrim: Scrim) -> None:
        """
        Adds/Fills the team to the scouting doc, then adds a page to the Scrim Results sheet

        Args:
            scrim (Scrim): The scrim request to accept
            accept (bool): Whether or not to accept the request

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs"""

        payload = {
            "function": "foundScrim",
            "parameters": [scrim.team.name, scrim.team.number, scrim.team.opggLink, scrim.time.strftime("%m/%d/%Y"), scrim.scrim_format.games, scrim.scrim_format.format_long],
            "devMode": True
        }
        await self._make_call(payload)

    async def cancel_scrim(self, scrim: Scrim) -> None:
        """
        Removes scrim from the scrim results sheet

        Args:
            scrim (Scrim): The scrim request to accept

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """

        payload = {
            "function": "cancelScrim",
            "parameters": [scrim.team.name, scrim.time.strftime("%m/%d/%Y")],
            "devMode": True
        }
        await self._make_call(payload)

    async def update_scrim_results(self) -> None:
        """
        Updates the scrim results sheet, should be called after a scrim block is played

        Args:
            None

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """

        payload = {
            "function": "updateScrimResults",
            "devMode": True
        }
        await self._make_call(payload)

    async def reset_scrim_results_data(self) -> None:
        """
        Reloads all of the scrim result data, this takes a while

        Args:
            None

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """

        payload = {
            "function": "resetScrimResultsData",
            "devMode": True
        }
        await self._make_call(payload)

    async def reset_scouting_scrim_results(self) -> None:
        """
        Reloads all of the scrim results in the scouting reports

        Args:
            None

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """

        payload = {
            "function": "resetScoutingScrimResults",
            "devMode": True
        }
        await self._make_call(payload)

if __name__ == "__main__":
    GoogleAPI().setup_creds()