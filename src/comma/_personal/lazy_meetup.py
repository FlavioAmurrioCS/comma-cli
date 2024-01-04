# flake8: noqa: PLR2004
from __future__ import annotations

import atexit
import datetime
import logging
import os
import pickle
import time
from dataclasses import dataclass
from dataclasses import field
from functools import lru_cache
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import typer
from rich.logging import RichHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from twilio.rest import Client

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement
    from selenium.webdriver.remote.webdriver import WebDriver
###############################################################################

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler()],
    # handlers=[RichHandler(rich_tracebacks=True, tracebacks_suppress=[selenium])]
)
logging.getLogger("selenium").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("twilio").setLevel(logging.ERROR)

# log = logging.getLogger("rich")
# log.info("Hello, World!")
###############################################################################


@dataclass
class QuickEvent:
    title: str
    status: str
    time_str: str
    address: str
    date: datetime.datetime = field(repr=False)
    link: str = field(repr=True)
    count: str

    def __init__(self, li_element: WebElement) -> None:
        time_element = li_element.find_element(By.TAG_NAME, "time")
        time_str = time_element.text
        title_elem = li_element.find_element(By.CLASS_NAME, "eventCardHead--title")

        self.address = li_element.find_element(By.TAG_NAME, "address").text
        self.title = title_elem.text
        self.link = title_elem.get_attribute("href") or ""
        self.status = li_element.find_element(By.CLASS_NAME, "eventCard--clickable").text
        self.time_str = time_element.text
        self.date = datetime.datetime.strptime(time_str, "%a, %b %d, %Y, %I:%M %p EDT")  # noqa: DTZ007

        attending_elem = li_element.find_elements(By.CLASS_NAME, "avatarRow--attendingCount")
        self.count = "0" if not attending_elem else attending_elem[0].text

    def should_process_event(self) -> bool:
        if self.status == "Going":
            logging.debug("Already going: %s", self)
            return False
        if self.status == "Waitlist":
            logging.debug("Already Waitlisted: %s", self)
            return False
        if self.date.weekday() < 5 and (self.date.hour < 16 or self.date.hour > 21):
            logging.debug("Can't go: %s", self)
            return False
        if (self.date - datetime.datetime.today()).days > 7:  # noqa: DTZ002
            logging.debug("Too much into the future: %s", self)
            return False
        if int(self.count.split()[0]) > 15:
            logging.debug("Too many attendees: %s", self)
            return False
        return True

    def text_msg(self) -> str:
        return dedent(
            f"""\
            {self.title}
            {self.time_str}
            {self.count}
            {self.link}"""
        )


@dataclass(unsafe_hash=True)
class Meetup:
    username: str
    password: str
    webdriver: WebDriver = field(hash=False)
    cookies_file: str
    # meetups: tuple[str, ...]

    def __post_init__(self) -> None:
        atexit.register(self.close_driver)
        self.load_cookies()

    def close_driver(self) -> None:
        self.save_cookies()
        logging.debug("Closing driver")
        self.webdriver.close()

    def load_cookies(self) -> None:
        if os.path.exists(self.cookies_file):
            self.webdriver.get("https://www.meetup.com/")
            with open(self.cookies_file, "rb") as f:
                logging.debug("Loading cookies...")
                cookies = pickle.load(f)  # noqa: S301
                for cookie in cookies:
                    self.webdriver.add_cookie(cookie)

    def save_cookies(self) -> None:
        with open(self.cookies_file, "wb") as f:
            logging.debug("Saving cookies.")
            pickle.dump(self.webdriver.get_cookies(), f)

    @lru_cache  # noqa: B019
    def ensure_login(self) -> None:
        self.webdriver.get("https://www.meetup.com/")
        if self.webdriver.find_elements(By.ID, "login-link"):
            logging.info("Trying to log in.")
            time.sleep(2)
            self.webdriver.find_element(By.ID, "login-link").click()

            email_input = self.webdriver.find_element(By.ID, "email")
            time.sleep(2)
            email_input.send_keys(self.username)

            password_input = self.webdriver.find_element(By.ID, "current-password")
            time.sleep(3)
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.RETURN)

            time.sleep(10)
            self.save_cookies()
            time.sleep(10)
        else:
            logging.debug("No login-link found, assuming we are already logged in.")

    def list_eligible_group_events(self, group_id: str) -> list[QuickEvent]:
        self.ensure_login()
        events_url = f"https://www.meetup.com/{group_id}/events/"
        # logging.debug(f'Scraping: {events_url}')
        self.webdriver.get(events_url)

        available_events_li = self.webdriver.find_elements(
            By.CSS_SELECTOR,
            ".eventList-list .list-item",
        )

        if len(available_events_li) > 8:
            # self.scroll_load_all()
            self.webdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            available_events_li = self.webdriver.find_elements(
                By.CSS_SELECTOR,
                ".eventList-list .list-item",
            )

        events = [QuickEvent(x) for x in available_events_li]
        total_events_count = len(events)
        events = [x for x in events if x.should_process_event()]
        eligible_events_count = len(events)
        logging.info(
            f"{events_url}. Scrapped: {total_events_count}. Eligible: {eligible_events_count}.",  # noqa: G004
        )

        return events

    # def list_events(self) -> list[QuickEvent]:
    #     # self.webdriver.find_elements(By.CSS_SELECTOR, '.eventList-list .eventCard--link')
    #     # document.querySelectorAll('.eventList-list .eventCard--link')
    #     self.ensure_login()

    #     all_events = []
    #     for mid in sorted(set(self.meetups)):
    #         events_url = f'https://www.meetup.com/{mid}/events/'
    #         logging.debug(f'Parsing {mid}...')
    #         self.webdriver.get(events_url)

    #         if len(self.webdriver.find_elements(By.CSS_SELECTOR, '.eventList-list .list-item')) > 8:  # noqa: E501
    #             self.scroll_load_all()

    #         available_events_li = self.webdriver.find_elements(
    #             By.CSS_SELECTOR, '.eventList-list .list-item',
    #         )

    #         events = [QuickEvent(x) for x in available_events_li]

    #         all_events.extend(events)
    #     return all_events

    # def scroll_load_all(self):
    #     SCROLL_PAUSE_TIME = 3

    #     # Get scroll height
    #     last_height = self.webdriver.execute_script('return document.body.scrollHeight')

    #     while True:
    #         # Scroll down to bottom
    #         self.webdriver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    #         # Wait to load page
    #         time.sleep(SCROLL_PAUSE_TIME)

    #         # Calculate new scroll height and compare with last scroll height
    #         new_height = self.webdriver.execute_script('return document.body.scrollHeight')
    #         if new_height == last_height:
    #             break
    #         logging.debug('Scroll again')
    #         last_height = new_height


def send_sms(tel_num: str, msg: str) -> None:
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=msg,
        from_=os.environ["TWILIO_PHONE_NUMBER"],
        # media_url=['https://demo.twilio.com/owl.png'],
        to=tel_num,
    )
    logging.debug(message.sid)


app = typer.Typer()


@app.command()
def main() -> None:
    username = ""
    passsword = ""
    meetings = (
        "braddock-rd-wallyball",  # AB+
        "fairfax-herndon-rec-wallyball-meetup",  # Regular Wally
        # 'fairfaxvolleyball',
    )
    options = FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(
        options=options,
        # executable_path='/snap/bin/geckodriver',  # type: ignore
    )
    meetup = Meetup(
        username=username,
        password=passsword,
        # meetups=meetings,
        webdriver=driver,
        cookies_file=(Path.home() / ".meetup_cookies.pickle").as_posix(),
    )

    for meeting in meetings:
        for e in meetup.list_eligible_group_events(meeting):
            send_sms("", e.text_msg())
            logging.error(e)


# https://www.meetup.com/fairfax-herndon-rec-wallyball-meetup/events/
# https://www.meetup.com/braddock-rd-wallyball/events/
# https://www.meetup.com/fairfaxvolleyball/events/
# eventList-list
# if __name__ == '__main__':
#     send_sms('', '')
