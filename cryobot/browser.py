from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException 
import re
from datetime import datetime

import pathlib
import traceback
from helper import debugPrint, getVariable
from scrim_classes import Scrim, ScrimFormat, Team
from time import sleep


TEAM_LINK: str = getVariable("TEAM_LINK")

class Browser:
    a = "Hi"
    def __init__(self):
        self._options = Options()
        self._options.add_argument("--start-maximized")
        self._options.add_argument(f"--user-data-dir={pathlib.Path().resolve()}/ChromeProfile")
        self._options.add_argument("--profile-directory=Default")
        self._options.add_argument("--log-level=3")
        self._options.add_argument("--silent")
        self._options.add_experimental_option('excludeSwitches', ['enable-logging'])

        self._driver: webdriver.Chrome = None

    def __del__(self):
        if isinstance(self._driver, webdriver.Chrome):
            self._driver.quit()

    def _handle_driver(func):
        def wrapper(self: "Browser", *args, **kwargs):
            try:
                # Open To Cryobark Page And Wait For It To Load
                self._driver = webdriver.Chrome(options=self._options)
                self._driver.get(TEAM_LINK)
                WebDriverWait(self._driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[contains(@class, 'TeamPanel') and text()='Cryobark']")))

                return func(self, *args, **kwargs) 
            except WebDriverException as e:
                lines = ""
                for line in traceback.format_tb(e.__traceback__ ):
                    lines += line
                debugPrint(lines)
                debugPrint(f"{type(e).__name__}: {e.msg}")
            except Exception as e:
                lines = ""
                for line in traceback.format_tb(e.__traceback__ ):
                    lines += line
                debugPrint(lines)
                debugPrint(f"{type(e).__name__}: {e}")
            finally:
                # Quit Web Driver
                self._driver.quit()
                self._driver = None
        return wrapper

    @_handle_driver
    def login(self):
        # DOESNT WORK since browser is controlled by test software D:
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
    def retrieve_incoming_scrim_requests(self) -> list[Scrim]:
        """
        Retrieves a list of current scrim requests

        Returns:
            list[Scrim]: List of currently open scrim requests
        """
        scrims = []

        # Click Notification Button -> Wait For Notification Page To Appear
        self._driver.find_element(By.XPATH, "//span[.//*[contains(@*, '#icon-bell')]]").click()
        WebDriverWait(self._driver, 3).until(expected_conditions.presence_of_element_located((By.XPATH, "//span[text()=\"That's it...\"]")))

        # Find Sent Scrim Request Notifications And Loop
        notificationXPath = "//div[./div[contains(@class, 'NotificationMarker')] and .//div[contains(text(), 'sent a scrim request')]]"
        notifications = self._driver.find_elements(By.XPATH, notificationXPath)
        for i in range(1, len(notifications) + 1):
            # Link (href="https://lol.gankster.gg/teams/teamNumber/teamname")  Text: teamName
            team_link = self._driver.find_element(By.XPATH, f"({notificationXPath}//div[contains(text(), 'sent a scrim request')]/a)[%d]" % i)
            team = Team(number=team_link.get_attribute("href").split("/")[4], name=team_link.accessible_name)

            # Datetime and Format  Jan 1, 12:00am (ScrimFormat.format_short)
            date_time_format = self._driver.find_element(By.XPATH, f"({notificationXPath}//div[contains(@class, 'ScrimRequestActivityItem')]/span)[%d]" % i).text
            match = re.match(r"(.+?) \((.+)\)", date_time_format)
            time = datetime.strptime(match.group(1) + " 2025", "%b %d, %I:%M%p %Y")
            format = ScrimFormat.from_short(match.group(2))
            scrims.append(Scrim(time=time, scrim_format=format, team=team))

        return scrims

    @_handle_driver
    def retrieve_booked_scrim_requests(self) -> list[Scrim]:
        """
        Retrieves a list of current scrim requests

        Returns:
            list[Scrim]: List of currently booked scrim requests
        """
        scrims = []

        # Click Notification Button -> Wait For Notification Page To Appear
        self._driver.find_element(By.XPATH, "//span[.//*[contains(@*, '#icon-bell')]]").click()
        WebDriverWait(self._driver, 3).until(expected_conditions.presence_of_element_located((By.XPATH, "//span[text()=\"That's it...\"]")))

        # Find Sent Scrim Request Notifications And Loop
        notificationXPath = "//div[ ./div[contains(text(), 'Confirmed a scrim')]]"
        notifications = self._driver.find_elements(By.XPATH, notificationXPath)
        for i in range(1, len(notifications) + 1):
            # Link (href="https://lol.gankster.gg/teams/teamNumber/teamname")  Text: teamName
            team_link = self._driver.find_element(By.XPATH, f"({notificationXPath}//a)[%d]" % i)
            team = Team(number=team_link.get_attribute("href").split("/")[4], name=team_link.accessible_name)

            # Datetime and Format  Jan 1, 12:00am (ScrimFormat.format_short)
            date_time_format = self._driver.find_element(By.XPATH, f"({notificationXPath}//span)[%d]" % i).text
            match = re.match(r"(.+?) \((.+)\)", date_time_format)
            time = datetime.strptime(match.group(1) + " 2025", "%b %d, %I:%M%p %Y")
            format = ScrimFormat.from_short(match.group(2))
            scrims.append(Scrim(time=time, scrim_format=format, team=team, open=False))

        return scrims

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
        # Click Search Button -> Wait For Search Page To Appear
        self._driver.find_element(By.XPATH, "//span[.//*[contains(@*, '#icon-search')]]").click()
        WebDriverWait(self._driver, 3).until(expected_conditions.element_to_be_clickable((By.XPATH, "//input[@placeholder='Find Teams']")))

        # Enter Team Name
        self._driver.find_element(By.XPATH, "//input[@placeholder='Find Teams']").send_keys(team_name)

        # Wait For Search Results To Load
        WebDriverWait(self._driver, 1).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[contains(@class, 'SearchPanel')]//i[contains(@class, 'spinner')]")))
        WebDriverWait(self._driver, 5).until(expected_conditions.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'SearchPanel')]//i[contains(@class, 'spinner')]")))

        # Retrieve Team Link -> Parse Team Number
        team_link = self._driver.find_elements(By.XPATH, "//div[contains(@class, 'SearchResultItem')]//a")
        if len(team_link):
            return team_link[0].get_attribute("href").split("/")[4]
        else:
            print("Here")
        return ""

if __name__ == "__main__":
    # browser = Browser()
    # for _ in range(10):
    #     if browser.retrieve_team_number('TD Tidal') != "85190":
    #         print("Missed")
    # print(f"Team Link: {browser.retrieve_team_number('TD Tidal')}")
    # print(f"Team Link: {browser.retrieve_team_number('TestingT')}")
    # print(datetime.strptime("Jan 1, 12:00am 2025", "%b %d, %I:%M%p %Y"))
    # browser = Browser()
    # start = datetime.now()
    # browser.retrieve_scrim_requests()
    # end = datetime.now()
    # print(end - start)
    # browser.retrieve_scrim_requests()
    # print(datetime.now() - end)
    a = Browser().retrieve_booked_scrim_requests()
    # print("Done4")
    for aa in a:
        print(aa)