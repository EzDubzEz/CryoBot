from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException , TimeoutException
import re
from datetime import datetime, timedelta

import pathlib
import traceback
from helper import debugPrint, getVariable
from scrim_classes import Scrim, ScrimFormat, Team, CryoBotError, ErrorName
from time import sleep


TEAM_LINK: str = getVariable("TEAM_LINK")
DATETIME_CHARACTER: str = getVariable("DATETIME_CHARACTER")
CHROMEDRIVER_PATH: str = getVariable("CHROMEDRIVER_PATH")

class Browser:
    def __init__(self):
        self._options = Options()
        self._options.add_argument("--window-size=1920,1080")
        self._options.add_argument("--headless=new")
        self._options.add_argument("--no-sandbox")
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
        """ Decorator To Handle Selenium Errors And Rass/Passthrough CryoBotErrors """
        def wrapper(self: "Browser", *args, **kwargs):
            try:
                # Open To Cryobark Page And Wait For It To Load
                self._driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=self._options)
                self._driver.get(TEAM_LINK)

                # Wait For Cryobark Page To Load
                WebDriverWait(self._driver, 30).until(expected_conditions.invisibility_of_element_located((By.XPATH, "//span[@class='rs-loader-spin']")))
                # If Given 503 Service Unavailible Page
                if len(self._driver.find_elements(By.XPATH, "//div[contains(@class, 'UserInfoErrorPagestyled__SWrapper')]")):
                    raise CryoBotError(ErrorName.GANKSTER_UNAVAILIBLE, "oh no")
                WebDriverWait(self._driver, 30).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'TeamNameDiv')]")))

                return func(self, *args, **kwargs)
            except CryoBotError:
                raise
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
            None

        Raises:
            CryoBotError: If issue occurs
        """
        # Click Notification Button -> Wait For Notification Page To Appear
        self._driver.find_element(By.XPATH, "//span[.//*[contains(@*, '#icon-bell')]]").click()
        WebDriverWait(self._driver, 3).until(expected_conditions.presence_of_element_located((By.XPATH, "//span[text()=\"That's it...\"]")))

        # Find Sent Scrim Request Notifications And Loop
        notificationXPath = "//div[./div[contains(@class, 'NotificationMarker')] and .//div[contains(text(), 'sent a scrim request')]]"
        notificationXPath = f"//div[./div[contains(@class, 'NotificationMarker')] and .//div[contains(text(), 'sent a scrim request')] and .//a[text()='{scrim.team.name}'] and .//span[text()='{scrim.time.strftime(f'%b %{DATETIME_CHARACTER}d, %I:%M')}{scrim.time.strftime('%p').lower()} ({scrim.scrim_format.format_short})']]"
        notifications = self._driver.find_elements(By.XPATH, notificationXPath)
        if not len(notifications):
            raise CryoBotError(ErrorName.SCRIM_REQUEST_NOT_FOUND, f"scrim={scrim}, accept={accept}")
        if accept:
            self._driver.find_element(By.XPATH, f"{notificationXPath}//button[text()='Open']").click()
            WebDriverWait(self._driver, 3).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[@class='rs-modal-dialog']")))
            self._driver.find_element(By.XPATH, "//div[@class='rs-modal-dialog']//button[text()='Confirm']").click()
            try:
                WebDriverWait(self._driver, 10).until(expected_conditions.invisibility_of_element_located((By.XPATH, "//div[@class='rs-modal-dialog']")))
            except TimeoutException:
                raise CryoBotError(ErrorName.GANKSTER_FAILED, "function='process_scrim_request'")
        else:
            self._driver.find_element(By.XPATH, f"{notificationXPath}//button[text()='Decline']").click()
            try:
                WebDriverWait(self._driver, 10).until(expected_conditions.invisibility_of_element(notifications[0]))
            except TimeoutException:
                raise CryoBotError(ErrorName.GANKSTER_FAILED, "function='process_scrim_request'")

    @_handle_driver
    def retrieve_incoming_scrim_requests(self) -> list[Scrim]:
        """
        Retrieves a list of current scrim requests

        Returns:
            list[Scrim]: List of currently open scrim requests

        Raises:
            CryoBotError: If issue occurs
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

        Raises:
            CryoBotError: If issue occurs
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

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """
        # Click Search Button -> Wait For Scrim Page To Appear
        self._driver.find_element(By.XPATH, "//span[.//*[contains(@*, '#icon-flag')]]").click()
        WebDriverWait(self._driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'QuickLFS__Container')]")))

        # Set Date
        self._driver.find_element(By.XPATH, "//div[./div[text()='DAY']]//button").click()
        self._select_date(scrim.time)

        # Set Time
        self._driver.find_element(By.XPATH, "//div[./div[text()='TIME']]//a").click()
        sleep(1)
        self._driver.find_element(By.XPATH, f"//li[text()='{scrim.time.strftime(f'%{DATETIME_CHARACTER}I:%M %p')}']").click()

        # Fill In Format
        self._driver.find_element(By.XPATH, "//div[./div[text()='FORMAT']]//a").click()
        sleep(1)
        self._driver.find_element(By.XPATH, f"//a[text()='{scrim.scrim_format.format_short}']").click()

        # Create Request
        self._driver.find_element(By.XPATH, "//button[text()='Post  LFS']").click()

        # Wait For Successfull Creation
        try:
            WebDriverWait(self._driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[@class='rs-notification-title-with-icon' and text()='LFS Created!']")))
        except TimeoutException:
            raise CryoBotError(ErrorName.GANKSTER_FAILED, "function='process_scrim_request'")

    @_handle_driver
    def cancel_scrim_request(self, scrim: Scrim) -> None:
        """
        Cancels a scrim request

        Args:
            scrim (Scrim): The scrim request to cancel

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """
        # Wait For Scrim Section To Load
        WebDriverWait(self._driver, 5).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'LFSNowMarker__NowMarker')]|//div[contains(text(), 'public lfs will be listed here.')]")))

        # Look For Button To Cancel Specific Scrim Request
        cancel_button = self._driver.find_elements(By.XPATH, f"//div[contains(@class,'LFSList__DayBox') and text()='{scrim.time.strftime('%a, %d %b')}']/following-sibling::div[contains(@class,'PublicLFSItem') and preceding-sibling::div[contains(@class,'LFSList__DayBox')][1][text()='{scrim.time.strftime('%a, %d %b')}']][.//div[text()='{scrim.time.strftime(f'%{DATETIME_CHARACTER}H:%M %p').lower()}']]//button[text()='Change LFS']")
        if not cancel_button:
            raise CryoBotError(ErrorName.NO_SCRIM_BLOCK_FOUND, f"scrim={scrim}" )

        self._driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", cancel_button[0])
        sleep(1)
        cancel_button[0].click()

        # Click Delete On Popup
        self._driver.find_element(By.XPATH, "//div[@class='rs-modal-content']//button[text()='Delete LFS']").click()

        # Wait For Successfull Cancellation
        try:
            WebDriverWait(self._driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[@class='rs-notification-title-with-icon' and text()='LFS Deleted']")))
        except TimeoutException:
            raise CryoBotError(ErrorName.GANKSTER_FAILED, "function='process_scrim_request'")

    @_handle_driver
    def cancel_scrim_block(self, scrim: Scrim, message: str) -> None:
        """
        Cancels a scrim block

        Args:
            scrim (Scrim): The confirmed scrim block to cancel

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """
        # Wait For Scrim Section To Load
        WebDriverWait(self._driver, 5).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'LFSNowMarker__NowMarker')]|//div[contains(text(), 'public lfs will be listed here.')]")))

        # Look For Button To Cancel Specific Scrim
        cancel_button = self._driver.find_elements(By.XPATH, f"//div[contains(@class,'LFSList__DayBox') and text()='{scrim.time.strftime('%a, %d %b')}']/following-sibling::div[contains(@class,'PublicLFSItem') and preceding-sibling::div[contains(@class,'LFSList__DayBox')][1][text()='{scrim.time.strftime('%a, %d %b')}']][.//div[text()='{scrim.time.strftime(f'%{DATETIME_CHARACTER}H:%M %p').lower()}']]//button[text()='Confirmed']")
        if not cancel_button:
            raise CryoBotError(ErrorName.NO_SCRIM_BLOCK_FOUND, f"scrim={scrim}" )


        self._driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", cancel_button[0])
        sleep(1)
        cancel_button[0].click()

        # Click Cancel On Popup
        self._driver.find_element(By.XPATH, "//div[@class='rs-modal-content']//button[text()='Cancel Scrim']").click()

        # Enter Cancellation Reason
        self._driver.find_element(By.XPATH, "//div[@class='rs-modal-content']//textarea[@placeholder='Add cancellation reason to continue...']").send_keys(message)

        # Confirm Cancel
        self._driver.find_element(By.XPATH, "//div[@class='rs-modal-content']//button[text()='Cancel Scrim']").click()

        # Wait For Successfull Cancellation
        try:
            WebDriverWait(self._driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[@class='rs-notification-title-with-icon' and text()='ScrimCanceled']")))
        except TimeoutException:
            raise CryoBotError(ErrorName.GANKSTER_FAILED, "function='process_scrim_request'")

    @_handle_driver
    def send_scrim_request(self, scrim: Scrim) -> None:
        """
        Sends a scrim request to a given team

        Args:
            scrim (Scrim): The scrim request to send

        Returns:
            None

        Raises:
            CryoBotError: If issue occurs
        """
        # Click Search Button -> Wait For Scrim Page To Appear
        self._driver.find_element(By.XPATH, "//span[.//*[contains(@*, '#icon-flag')]]").click()
        WebDriverWait(self._driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'LfsListHeader')]")))

        start = datetime.now()
        # End After Finding Team, Reaching End, Or Timeout
        while not len(self._driver.find_elements(By.XPATH, f"//div[text()=\"That's it for now...\"] | //div[.//div[text()='{scrim.team.name}'] and contains(@class, 'PublicLFSItem')]//button")) and datetime.now() - start < timedelta(seconds=30):
            # Scroll Final Scrim Listing To Load More
            element = self._driver.find_element(By.XPATH, "(//div[contains(@class, 'LFSList__DayBox')])[last()]")
            self._driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)

            # Wait For More Teams To Load
            WebDriverWait(self._driver, 1).until(expected_conditions.visibility_of_element_located((By.XPATH, "//span[@class='rs-loader-spin']")))
            WebDriverWait(self._driver, 10).until(expected_conditions.invisibility_of_element_located((By.XPATH, "//span[@class='rs-loader-spin']")))

        opens = self._driver.find_elements(By.XPATH, f"//div[.//div[text()='{scrim.team.name}'] and contains(@class, 'PublicLFSItem')]//button")
        # Team Not Sending Out Scrim Request (No Premium D:)
        if not len(opens):
            raise CryoBotError(ErrorName.NO_TEAM_OUTGOING_SCRIM_REQUEST, fields=f"scrim={scrim}")

        # Scroll "Open" Button Into View And Wait
        self._driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", opens[0])
        sleep(1)

        # Click "Open" Button (To Create Scrim Request)
        self._driver.find_element(By.XPATH, f"//div[.//div[text()='{scrim.team.name}'] and contains(@class, 'PublicLFSItem')]//button").click()

        # Wait For Send Scrim Modal
        WebDriverWait(self._driver, 2).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[@class='rs-modal-dialog']")))

        # Set Time
        self._driver.find_element(By.XPATH, "//div[contains(@class, 'ScrimEventModal__TimeFlex')]//a").click()
        self._driver.find_element(By.XPATH, f"//li[text()='{scrim.time.strftime(f'%{DATETIME_CHARACTER}I:%M %p')}']").click()

        # Set Date
        self._driver.find_element(By.XPATH, "//div[contains(@class, 'ScrimEventModal__TimeFlex')]//div[contains(@class, 'DatePicker')]").click()
        self._select_date(scrim.time)

        # Fill In Format
        self._driver.find_element(By.XPATH, "//div[@class='rs-modal-dialog']//div[contains(@class, 'rs-picker-select')]").click()
        self._driver.find_element(By.XPATH, f"//a[text()='{scrim.scrim_format.format_short}']").click()

        # Send Request
        self._driver.find_element(By.XPATH, "//button[text()='Send Request']").click()
        try:
            WebDriverWait(self._driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[@class='rs-notification-title-with-icon' and text()='Scrim request sent!']")))
        except TimeoutException:
            raise CryoBotError(ErrorName.GANKSTER_FAILED, "function='process_scrim_request'")

    @_handle_driver
    def retrieve_team_number(self,team_name: str) -> str:
        """
        Retrieves the team number for a given team

        Args:
            team_name (str): The name of the team to search

        Returns:
            str: the team number for the given team

        Raises:
            CryoBotError: If issue occurs
        """
        # Click Search Button -> Wait For Search Page To Appear
        self._driver.find_element(By.XPATH, "//span[.//*[contains(@*, '#icon-search')]]").click()
        WebDriverWait(self._driver, 3).until(expected_conditions.element_to_be_clickable((By.XPATH, "//input[@placeholder='Find Teams']")))

        # Enter Team Name
        self._driver.find_element(By.XPATH, "//input[@placeholder='Find Teams']").send_keys(team_name)

        # Wait For Search Results To Load
        WebDriverWait(self._driver, 1).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'SearchPanel')]//i[contains(@class, 'spinner')]")))
        WebDriverWait(self._driver, 5).until(expected_conditions.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'SearchPanel')]//i[contains(@class, 'spinner')]")))

        # Retrieve Team Link -> Parse Team Number
        team_link = self._driver.find_elements(By.XPATH, "//div[contains(@class, 'SearchResultItem')]//a")
        if len(team_link):
            return team_link[0].get_attribute("href").split("/")[4]

        return ""

    def _select_date(self, date: datetime):
        start = datetime.now()
        # Navigate Calendar To Correct Month/Year
        while datetime.now() - start < timedelta(seconds=10):
            selected_date = datetime.strptime(self._driver.find_element(By.XPATH, "//div[@class='rs-calendar']//span[contains(@class, 'rs-calendar-header')]").text, "%b %d, %Y")
            if (selected_date.year, selected_date.month) < (date.year, date.month):
                self._driver.find_element(By.XPATH, "//i[@class='rs-calendar-header-forward']").click()
            elif (selected_date.year, selected_date.month) > (date.year, date.month):
                self._driver.find_element(By.XPATH, "//i[@class='rs-calendar-header-backward']").click()
            else:
                break

        # Select Date From Calendar
        self._driver.find_element(By.XPATH, f"//div[@title='{date.strftime('%b %d, %Y')}']//span").click()

if __name__ == "__main__":
    browser = Browser()
    # for _ in range(100):
    #     if browser.retrieve_team_number('TD Tidal') != "85190":
    #         print("Missed")
    # browser.send_scrim_request(Scrim(datetime.strptime('12/09/25 10:00', '%m/%d/%y %H:%M'), ScrimFormat.FOUR_GAMES, Team(name="TeamTrebo")))
    browser.cancel_scrim_request(Scrim(datetime.strptime('12/06/25 8:00', '%m/%d/%y %H:%M'), ScrimFormat.FOUR_GAMES, Team(name="TeamTrebo")))
    # browser.cancel_scrim_block(Scrim(datetime.strptime('10/07/25 10:00', '%m/%d/%y %H:%M'), ScrimFormat.FOUR_GAMES, Team(name="TeamTrebo")), "Cancellation")
    # browser.cancel_scrim_request(Scrim(datetime.strptime('10/07/25 10:00', '%m/%d/%y %H:%M'), ScrimFormat.FOUR_GAMES, Team(name="TeamTrebo")))
    # browser.process_scrim_request(Scrim(datetime.strptime('10/07/25 10:00', '%m/%d/%y %H:%M'), ScrimFormat.FOUR_GAMES, Team(name="TeamTrebo")), True) #TODO Test
    # browser.create_scrim_request(Scrim(datetime.strptime('09/07/25 10:00',
    #               '%m/%d/%y %H:%M'), ScrimFormat.BEST_OF_THREE))
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
    # a = Browser().retrieve_booked_scrim_requests()
    # # print("Done4")
    # for aa in a:
    #     print(aa)
