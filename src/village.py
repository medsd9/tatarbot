from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from .utils import log
from .util_game import close_modal
from .custom_driver import client, use_browser
from enum import Enum


class building(Enum):
    smithy = 13
    headquarter = 15
    rallypoint = 16
    market = 17
    barracks = 19
    academy = 22
    residence = 25

@use_browser
def open_village(browser: client, id: int) -> None:

    try:
        # check selected village
        ul = browser.find("//div[contains(@id, 'side_info')]")

        ul = ul.find_element(By.XPATH, ".//tbody")
        lis = ul.find_elements(By.XPATH, ".//tr")
        link = lis[id].find_element(By.XPATH, ".//a")
        browser.click(link, 1)
    except:

        pass

        # close_modal(browser)


def open_city(browser: client) -> None:
    btn = browser.find("//a[@id='n2']")

    browser.click(btn, 1)


def open_resources(browser: client) -> None:
    btn = browser.find("//a[@id='n1']")
    log("clik ressource")
    browser.click(btn, 1)


def open_building(browser: client, building: int) -> None:
    # todo open by slot id
    browser.get("https://qtatar.com/build?id={}".format(str(building)))


def open_building_type(browser: client, b_type: building) -> None:
    view = browser.find("//div[@id='villageView']")
    locations = view.find_elements(By.XPATH, ".//building-location")

    for loc in locations:
        classes = loc.get_attribute("class")

        if "free" not in classes:
            img = loc.ind_element(By.XPATH, ".//img")
            classes = img.get_attribute("class")
            class_list = classes.split(" ")

            for c in class_list:
                if c == "buildingId{}".format(b_type.value):
                    browser.click(img)
                    return


def open_map(browser: client) -> None:
    map_button = browser.find("//a[contains(@class, 'navi_map bubbleButton')]")
    browser.click(map_button, 1)
