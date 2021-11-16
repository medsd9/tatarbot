from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from .custom_driver import client, use_browser
from .village import open_village, open_city, open_resources
from .utils import log, parse_time_to_seconds
from .util_game import close_modal
from .settings import *
import time
import json
import os
import re


def master_builder_thread(
    browser: client, village: int, file_name: str, interval: int
) -> None:
    default_interval = interval
    browser.sleep(5)
    with open(settings.buildings_path, "r") as f:
        content = json.load(f)
    buildings = [x for x in content["buildings"]]
    file_path = os.path.join(BASE_DIR, "assets", file_name)
    # BASE_DIR come from settings.py
    while True:
        with open(file_path, "r") as f:
            content = json.load(f)
        queues = [x for x in content["queues"]]

        construct_slot = check_building_queue(browser, village)

        if queues and (construct_slot):
            while construct_slot:
                log('construct_slot' + str(construct_slot))

                if "depends" in queues[0] and construct_slot != 3:
                    log("dependant")
                    browser.sleep(30)
                    break
                else:
                    queues = master_builder(
                        browser, village, queues, buildings)
                    construct_slot = check_building_queue(
                        browser, village)
                    if not construct_slot:
                        endNow(browser, village)
                        construct_slot = check_building_queue(
                            browser, village)

                    if not queues:
                        break
            with open(file_path, "w") as f:
                f.write('{"queues":')
                f.write(json.dumps(queues or [], indent=4))
                f.write("}")

            time.sleep(interval)

        else:
            log("no queue or slot !")
            construct_slot = check_building_queue(browser, village)
            if not construct_slot:
                # interval, can_finish_earlier = check_queue_times(
                #     browser, village, default_interval
                # )
                time.sleep(interval)

                # if can_finish_earlier:
                #     five_mins(browser, village)
            elif not queues:
                log("Queues is empty, please add queue to {}".format(file_name))
                log(time.strftime("%H:%M"))
                time.sleep(default_interval)
            else:
                time.sleep(default_interval)


@use_browser
def master_builder(
    browser: client, village: int, queues: list, buildings: list
) -> list:
    open_village(browser, village)
    log("start build")

    if (
        "Village" in queues[0]["queueLocation"]
        and "Construct" in queues[0]["queueType"]
    ):
        log("cond 1 " + queues[0]["queueBuilding"])
        found = False
        for building in buildings:
            if queues[0]["queueBuilding"] in building["buildingName"]:
                building_id = building["buildingId"]
                found = True
                break
        if not found:
            log("buildingId not found, remove it from queues.")
            new_queues = queues[1:]
            return new_queues
        open_city(browser)

        time.sleep(1)
        buildMap = browser.find('//div[@id="village_map"]')
        if building_id == "16":
            log("BUILDING RALLY")
            browser.get("https://qtatar.com/build?id=39")
            browser.sleep(2)
        else:
            buildMap = browser.find('//map[@id="map2"]')
            buildPlace = buildMap.find_elements(By.XPATH,
                                                ".//area[@title ='موقع البناء']")
            log(buildPlace[0].get_attribute("href"))
            browser.get(buildPlace[0].get_attribute("href"))
        browser.sleep(2)
        buildPage = browser.find('//div[@class="gid0"]')

        btnBuild = buildPage.find_elements(
            By.XPATH, './/a[contains(@class,"build")]')
        for b in btnBuild:
            if "b={}".format(building_id) in b.get_attribute("href"):

                browser.click(b)
                new_queues = queues[1:]
                return new_queues
                break

        new_queues = queues[1:]
        return new_queues
    elif (
            "Upgrade" in queues[0]["queueType"] and "Village" in queues[0]["queueLocation"]):
        log("cond 2 " + queues[0]["queueBuilding"])

        open_city(browser)
        browser.sleep(1)
        found = False
        for building in buildings:
            if queues[0]["queueBuilding"] in building["buildingName"]:
                building_id = building["buildingId"]
                found = True
                break
        if not found:
            log("buildingId not found, remove it from queues.")
            new_queues = queues[1:]
            return new_queues
        browser.sleep(2)
        if building_id == "16":
            log("BUILDING RALLY")
            browser.get("https://qtatar.com/build?id=39")
            browser.sleep(2)
            box = browser.find('//p[@id="contract"]')
            if box.find_elements(
                    By.XPATH, ".//span[contains(@class,'none')]") and not box.find_elements(
                    By.XPATH, ".//a[contains(@class,'build')]"):
                new_queues = queues[1:]
                return new_queues
            btn = box.find_elements(
                By.XPATH, ".//a[contains(@class,'build')]")

            browser.click(btn[0], 1)

            new_queues = queues[1:]

            return new_queues

        else:
            buildMap = browser.find('//div[@id="village_map"]')
            buildPlace = buildMap.find_elements(
                By.XPATH, ".//img[contains(@class,'building')]")
            for id , item in enumerate(buildPlace):
                if "g{}".format(building_id) in item.get_attribute("class"):

                    if "20" not in item.get_attribute("alt"):
                        log("FOUND BAT")
                        browser.click(item, 3)
                        browser.sleep(2)
                        box = browser.find('//p[@id="contract"]')

                        btn = box.find_elements(
                            By.XPATH, ".//a[contains(@class,'build')]")
                        for b in btn:

                            if "max" in b.get_attribute("href"):
                                new_queues = queues[1:]
                                return new_queues
                            else:
                                browser.click(b, 1)

                                new_queues = queues[1:]

                                return new_queues

            new_queues = queues[1:]

            return new_queues
    elif "Resources" in queues[0]["queueLocation"]:
        log("cond 3 " + queues[0]["queueBuilding"])

        open_resources(browser)
        time.sleep(1)
        location_id = queues[0]["queueBuilding"]

        base_url = "https://qtatar.com"
        base_url += "/build?id="
        base_url += location_id
        log(base_url)
        browser.get(base_url)
        time.sleep(3)
        try:
            divId = browser.find('//div[@id ="build"]')
            btn = divId.find_element(By.XPATH, './/a[@class="build"]')
            browser.click(btn, 1)
            new_queues = queues[1:]
            log("building ressource")
            return new_queues
        except:

            new_queues = queues[1:]

            return new_queues

    else:
        return queues


@ use_browser
def check_queue_times(browser: client, village: int, default_interval: int) -> tuple:
    open_village(browser, village)
    construct_slot, queue_slot = check_building_queue(browser, village)
    if construct_slot:
        return default_interval, False
    # writedown the time
    building_queue_container = browser.find(
        '//div[contains(@class, "buildingQueueContainer queueContainer")]'
    )
    divs = building_queue_container.find_elements(By.XPATH, "./div")
    for div in divs:
        the_class = div.get_attribute("drop-class")
        if not the_class:
            continue
        else:
            if "noDrop" in the_class:
                browser.click(div, 1)
                inner_box = browser.find('//div[@class="detailsInnerBox"]')
                details_contents = inner_box.find_elements(By.XPATH,
                                                           './div[contains(@class, "detailsContent")]'
                                                           )
                times = []
                finish_earlier = []
                for details_content in details_contents:
                    details_info = details_content.find_element(By.XPATH,
                                                                './div[contains(@class, "detailsInfo")]'
                                                                )
                    details_time = details_info.find_element(By.XPATH,
                                                             './div[@class="detailsTime"]'
                                                             )
                    span = details_time.find_element(By.XPATH, "./span")
                    the_time = span.get_attribute("innerHTML")
                    times.append(the_time)
                    details_button = details_content.find_element(By.XPATH,
                                                                  './div[contains(@class, "detailsButtonContainer")]'
                                                                  )
                    button = details_button.find_element(By.XPATH, "./button")
                    the_class = button.get_attribute("class")
                    if "disabled" in the_class:
                        finish_earlier.append(False)
                    else:
                        finish_earlier.append(True)
                break
            else:
                continue
    # parse time to seconds
    times_in_seconds = []
    for time in times:
        time_in_seconds = parse_time_to_seconds(time)
        times_in_seconds.append(time_in_seconds)
    if len(times_in_seconds) > 1:
        if times_in_seconds[0] < times_in_seconds[1]:
            if times_in_seconds[0] < 300 and finish_earlier[0]:
                return 1, True
            elif times_in_seconds[0] > 300 and finish_earlier[0]:
                return times_in_seconds[0] - 298, True
            else:
                return times_in_seconds[0], False
        elif times_in_seconds[0] > times_in_seconds[1]:
            if times_in_seconds[1] < 300:
                return 1, True
            else:
                return times_in_seconds[1] - 298, True
        else:
            if times_in_seconds[1] < 300:
                return 1, True
            else:
                return times_in_seconds[1] - 298, True
    else:
        if times_in_seconds[0] < 300 and finish_earlier[0]:
            return 1, True
        elif times_in_seconds[0] > 300 and finish_earlier[0]:
            return times_in_seconds[0] - 298, True
        elif not finish_earlier[0]:
            return times_in_seconds[0] + 1, False

    return 1, True


@ use_browser
def check_building_queue(browser: client, village: int) -> tuple:
    open_village(browser, village)
    # check how much construction slot that empty
    try:
        construction_container = browser.find(
            './/table[@id="building_contract"]')
        log("queue finded !")
        tbody = construction_container.find_element(
            By.XPATH, './/tbody')

        building_queue_slots = tbody.find_elements(
            By.XPATH, "./tr")

        log('building_queue_slots {}' + format(len(building_queue_slots)))
        return 3 - len(building_queue_slots)

    except NoSuchElementException:
        return 3


# def roman_constructor(
#     browser: client, village: int, queues: list, buildings: list
# ) -> list:
#     temp_dict = {x: y for x, y in enumerate(queues)}
#     new_dict = {x: y for x, y in enumerate(queues)}
#     for index, queue in temp_dict.items():
#         if "Village" in queue["queueLocation"] and "Construct" in queue["queueType"]:
#             temp_queues = [queue]
#             new_queues = master_constructor(browser, temp_queues, buildings)
#             if not new_queues:
#                 del new_dict[index]
#             construct_slot, queue_slot = check_building_queue(browser, village)
#             if not construct_slot and not queue_slot:
#                 break
#         elif "Village" in queue["queueLocation"] and "Upgrade" in queue["queueType"]:
#             open_city(browser)
#             time.sleep(1)
#             for building in buildings:
#                 if queue["queueBuilding"] in building["buildingName"]:
#                     building_id = building["buildingId"]
#                     break
#             building_img = browser.find(
#                 '//img[contains(@class, "{}")]/following::span'.format(building_id)
#             )
#             building_status = building_img.find_element(By.XPATH,
#                                                         './/div[contains(@class, "buildingStatus")]'
#                                                         )
#             color = building_status.find_element(By.XPATH,
#                                                  './/div[contains(@class, "colorLayer")]'
#                                                  ).get_attribute("class")
#             temp_queues = [queue]
#             new_queues = check_color(
#                 browser, village, color, building_status, temp_queues
#             )
#             if not new_queues:
#                 del new_dict[index]
#             construct_slot, queue_slot = check_building_queue(browser, village)
#             if not construct_slot and not queue_slot:
#                 break
#         elif "Resources" in queue["queueLocation"]:
#             open_resources(browser)
#             time.sleep(1)
#             location_id = queue["queueBuilding"]
#             building_location = browser.find(
#                 '//building-location[@class="buildingLocation {}"]'.format(
#                     location_id)
#             )
#             building_status = building_location.find_element(By.XPATH,
#                                                              './/div[contains(@class, "buildingStatus")]'
#                                                              )
#             color = building_status.find_element(By.XPATH,
#                                                  './/div[contains(@class, "colorLayer")]'
#                                                  ).get_attribute("class")
#             temp_queues = [queue]
#             new_queues = check_color(
#                 browser, village, color, building_status, temp_queues
#             )
#             if not new_queues:
#                 del new_dict[index]
#             construct_slot, queue_slot = check_building_queue(browser, village)
#             if not construct_slot and not queue_slot:
#                 open_city(browser)
#                 break
#     new_queue = [x for x in new_dict.values()]
#     return new_queue


def endNow(browser: client, village: int) -> None:
    open_resources(browser)
    construct_slot = check_building_queue(browser, village)
    if construct_slot != 0:
        return

    try:
        construction_container = browser.find(
            './/table[@id="building_contract"]')
        log("queue finded !")
        tbody = construction_container.find_element(
            By.XPATH, './/tbody')

        building_queue_slots = tbody.find_elements(
            By.XPATH, "//span[@id='timer1']")
        sum = 0
        for b in building_queue_slots:

            sum += parse_time_to_seconds(b.get_attribute("innerHTML"))

        if sum > 60*10:
            thead = construction_container.find_element(
                By.XPATH, './/thead')
            btn = thead.find_element(By.XPATH, './/a')
            browser.click(btn)

    except NoSuchElementException:
        return


def five_mins(browser: client, village: int) -> None:
    notepad = browser.find('//a[@id="notepadButton"]')
    construct_slot, queue_slot = check_building_queue(browser, village)
    if construct_slot:
        browser.hover(notepad)
        return
    building_queue_container = browser.find(
        '//div[contains(@class, "buildingQueueContainer queueContainer")]'
    )
    divs = building_queue_container.find_elements(By.XPATH, "./div")
    for div in divs:
        the_class = div.get_attribute("drop-class")
        if not the_class:
            continue
        else:
            if "noDrop" in the_class:
                browser.click(div, 1)
                inner_box = browser.find('//div[@class="detailsInnerBox"]')
                details_contents = inner_box.find_elements(By.XPATH,
                                                           './div[contains(@class, "detailsContent")]'
                                                           )
                for details_content in details_contents:
                    details_button = details_content.find_element(By.XPATH,
                                                                  './div[contains(@class, "detailsButtonContainer")]'
                                                                  )
                    button = details_button.find_element(By.XPATH, "./button")
                    the_class = button.get_attribute("class")
                    if "disabled" in the_class or "premium" in the_class:
                        continue
                    else:
                        try:
                            voucher = button.find_element(By.XPATH,
                                                          './/span[@class="price voucher"]'
                                                          )
                        except:
                            browser.click(button, 1)
                        else:
                            continue
                break
            else:
                continue
