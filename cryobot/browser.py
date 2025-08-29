from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import pathlib
import traceback
from helper import debugPrint, getVariable
from scrim_classes import Scrim

TEAM_LINK = getVariable("TEAM_LINK")

class Browser:
    def __init__(self):
        self._options = Options()
        self._options.add_argument("--start-maximized")
        self._options.add_argument(f"--user-data-dir={pathlib.Path().resolve()}/ChromeProfile")
        self._options.add_argument("--profile-directory=Default")
        self._options.add_argument("--log-level=3")
        self._options.add_argument("--silent")

        # self._driver = webdriver.Chrome(options=self._options)
        self._driver: webdriver.Chrome = None

    def __del__(self):
        if isinstance(self._driver, webdriver.Chrome):
            self._driver.quit()

    def _handle_driver(func):
        def wrapper(self, *args, **kwargs):
            try:
                self._driver = webdriver.Chrome(options=self._options)
                self._driver.get(TEAM_LINK)
                return func(self, *args, **kwargs)
            except Exception as e:
                debugPrint(f"SeleniumError: {e}")
                traceback.print_exc()
            finally:
                self._driver.quit()
        return wrapper

    @_handle_driver
    def login(self):
        self._driver.get("https://lol.gankster.gg/login")
        if self._driver.current_url != "https://lol.gankster.gg/login":
            self._driver.find_element(By.XPATH, "//div[contains(@class, 'UserSections')]").click()
            account = self._driver.find_element(By.XPATH, "//div[contains(@class, 'UserSectionList') and contains(@class, 'Header')]//div[text()]").text
            print(f"Already Logged In As {account}, Please Logout To Continue")
            return
        riotLink = self._driver.find_element(By.XPATH, "//a[text()='Continue with Riot']").get_attribute("href")
        self._driver.get(riotLink)

        # Since gankster uses riot login, and riot has 2FA, this needs to be done manually, wait until user logs in then be happy
        wait = WebDriverWait(self._driver, 60)
        wait.until(expected_conditions.url_contains("https://lol.gankster.gg/"))

    @_handle_driver
    def process_scrim_request(self, scrim: Scrim, accept:bool=True) -> bool:
        """
        Accepts/Declines the given scrim request

        Args:
            scrim (Scrim): The scrim request to accept
            accept (bool): Whether or not to accept the request

        Returns:
            bool: Whether or not the given scrim was found
        """
        return

    @_handle_driver
    def retrieve_scrim_requests(self) -> list[Scrim]:
        """
        Retrieves a list of current scrim requests

        Returns:
            list[Scrim]: List of currently open scrim requests
        """
        return

    @_handle_driver
    def create_scrim_request(self, scrim: Scrim) -> None:
        """
        Creates a scrim request

        Args:
            scrim (Scrim): The scrim request to create
        """
        return

    @_handle_driver
    def cancel_scrim_request(self, scrim: Scrim) -> None:
        """
        Cancels a scrim request

        Args:
            scrim (Scrim): The scrim request to cancel
        """
        return

    @_handle_driver
    def cancel_all_scrim_requests(self, scrim: Scrim) -> None:
        """
        Cancels a scrim request

        Args:
            scrim (Scrim): The scrim request to cancel
        """
        return

    @_handle_driver
    def send_scrim_request(self, scrim: Scrim) -> None:
        """
        Cancels a scrim request

        Args:
            scrim (Scrim): The scrim request to cancel
        """
        return

    @_handle_driver
    def retrieve_team_number(self,team_name: str) -> str:
        """
        Retrieves the team number for a given team

        Args:
            team_name (str): The name of the team to search

        Returns:
            str: the team number for the given team
        """
        return

if __name__ == "__main__":
    Browser().login()