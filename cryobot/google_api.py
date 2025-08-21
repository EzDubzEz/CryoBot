from helper import getVariable
from scrim_classes import Scrim, ScrimFormat, Team
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pathlib
import subprocess
from datetime import datetime

GOOGLE_SCOPES = getVariable("GOOGLE_SCOPES")
CLIENT_ID = getVariable("CLIENT_ID")
CLIENT_SECRET = getVariable("CLIENT_SECRET")
GOOGLE_URL = getVariable("GOOGLE_URL")

class GoogleAPI:
    def __init__(self):
        self._creds = self._getCreds()
        if self._creds != None:
            self._headers = {"Authorization": f"Bearer {self._creds.token}","Content-Type": "application/json"}
        pass

    def _getCreds(self) -> Credentials:
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

        return creds

    def setupCreds(self) -> None:
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

    def isAuthSetup(self) -> bool:
        return self._creds != None

    def _make_call(self, payload):
        response = requests.post(GOOGLE_URL, headers=self._headers, json=payload)

        # TODO: Handle response.status_code
        print(response.status_code)
        print(response.text)
        return response.text #res

    def setupScrim(self, scrim: Scrim) -> None:
        """
        Adds/Fills the team to the scouting doc, then adds a page to the Scrim Results sheet

        Args:
            scrim (Scrim): The scrim request to accept
            accept (bool): Whether or not to accept the request

        Returns:
            None

        Raises:
            CryoBotError: If script fails"""

        payload = {
            "function": "scrimFound",
            "parameters": [scrim.team.name, f"https://lol.gankster.gg/teams/{scrim.team.number}", scrim.team.opggLink, scrim.time.strftime("%m/%d/%Y"), scrim.scrimFormat.value],
            "devMode": True  # always run the latest code
        }
        response = self._make_call(payload)

    def updateScrimResults(self) -> None:
        """
        Updates the scrim results sheet to be called after a scrim block is played

        Args:
            scrim (Scrim): The scrim request to accept
            accept (bool): Whether or not to accept the request

        Returns:
            None

        Raises:
            CryoBotError: If script fails"""
        payload = {
            "function": "updateScrimResults",
            "devMode": True
        }
        response = self._make_call(payload)
    pass

if __name__ == "__main__":
    team = Team("84830", "Cryoborkers", opggLink="https://op.gg/lol/summoners/na/TreboTehTree-NA1")
    scrim = Scrim(datetime.now(), ScrimFormat.THREE_GAMES, team=team)
    # GoogleAPI().setupScrim(scrim)
    GoogleAPI().updateScrimResults()