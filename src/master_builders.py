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
    # browser.sleep(10)
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
                queues = master_builder(browser, village, queues, buildings)
                construct_slot = check_building_queue(
                    browser, village)
                if not construct_slot:
                    break
                if not queues:
                    break
            with open(file_path, "w") as f:
                f.write('{"queues":')
                f.write(json.dumps(queues, indent=4))
                f.write("}")
            # interval, can_finish_earlier = check_queue_times(
            #     browser, village, default_interval
            # )
            time.sleep(interval)
            # if can_finish_earlier:
            #     five_mins(browser, village)
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
        log("construct 1")
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
        browser.sleep(3)
        buildMap = browser.find('//div[@id="village_map"]')
        buildPlace = buildMap.find_elements(
            By.XPATH, ".//img[contains(@class,'building')]")
        log(format(len(buildPlace)))
        for n in buildPlace:

            if "iso" in n.get_attribute("class"):
                browser.click(n, 1)
                log(n.get_attribute("class"))
                browser.sleep(3)
                buildPage = browser.find('//div[@class="gid0"]')
                tables = buildPage.find_elements(
                    By.XPATH, '//table[@class="new_building"]')
                for t in tables:

                    btnBuild = t.find_elements(By.XPATH, './/a')
                    for a in btnBuild:
                        if "build" in a.get_attribute("class"):
                            log("5")

                            if "b={}".format(building_id) in a.get_attribute("href"):
                                log("6")
                                browser.click(a)
                                new_queues = queues[1:]
                                return new_queues
                                break

                new_queues = queues[1:]
                return new_queues
    elif (
            "Upgrade" in queues[0]["queueType"] and "Village" in queues[0]["queueLocation"]):
        log("cond 2 ")

        open_city(browser)
        time.sleep(1)
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

        buildMap = browser.find('//div[@id="village_map"]')
        buildPlace = buildMap.find_elements(
            By.XPATH, ".//img[contains(@class,'building')]")
        for item in buildPlace:
            n = item
            if "g{}".format(building_id) in item.get_attribute("class"):
                if "20" not in item.get_attribute("alt"):
                    browser.click(n)
                    box = browser.find('//div[@id="build"]')

                    btn = box.find_elements(
                        By.XPATH, ".//a")
                    for a in btn:
                        if "build" in a.get_attribute("class"):
                            
                            new_queues = queues[1:]
                            log("building ressource")
                            return new_queues

    elif "Resources" in queues[0]["queueLocation"]:
        log("cond 3")

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
    browser.hover(notepad)
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


@ use_browser
def master_constructor(browser: client, queues: list, buildings: list) -> list:
    open_city(browser)
    time.sleep(1)
    base_url = browser.current_url()
    location_slots = browser.finds(
        '//building-location[contains(@class, "free")]')

    if len(location_slots) < 1:
        log("no free slot for construc the building.")
        new_queues = queues[1:]
        return new_queues

    the_class = location_slots[0].get_attribute("class")
    base_url += "/location:"
    base_url += re.findall("\d+", the_class)[0]
    base_url += "/window:building"
    browser.get(base_url)
    time.sleep(3.5)
    found = False

    for building in buildings:
        if queues[0]["queueBuilding"] in building["buildingName"]:
            building_type = building["buildingType"]
            found = True
            break

    if not found:
        log("buildingType not found, remove it from queues.")
        new_queues = queues[1:]
        return new_queues

    modal_content = browser.find('//div[@class="modalContent"]')
    pages = modal_content.find_element(
        By.XPATH, './/div[contains(@class, "pages")]')
    pages_class = pages.get_attribute("class")
    found = False
    if "ng-hide" in pages_class:
        building_img = modal_content.find_elements(By.XPATH, ".//img")
        for img in building_img:
            the_class = img.get_attribute("class")
            if building_type in the_class:
                browser.click(img, 1)
                found = True
                break
    else:
        pages = pages.find_elements(By.XPATH, "./div")
        for page in pages[2:-1]:
            building_img = modal_content.find_elements(By.XPATH, ".//img")
            for img in building_img:
                the_class = img.get_attribute("class")
                if building_type in the_class:
                    browser.click(img, 1)
                    found = True
                    break
            if found:
                break
            browser.click(pages[-1], 1.3)
    if not found:
        log("building image not found.")
        close_modal(browser)
        new_queues = queues[1:]
        return new_queues

    buttons = modal_content.find_elements(By.XPATH,
                                          './/button[contains(@class, "startConstruction")]'
                                          )

    for button in buttons:
        the_class = button.get_attribute("class")
        if "ng-hide" not in the_class:
            if "disable" in the_class:
                tooltip = button.get_attribute("tooltip-translate-switch")
                if "Requirements" in tooltip:
                    log("requirements not fulfilled.")
                    close_modal(browser)
                    new_queues = queues[1:]
                    return new_queues
                else:
                    log("building queue full.")
                    close_modal(browser)
                    return queues
            else:
                browser.click(button, 1.3)
                log("constructing..")
                new_queues = queues[1:]
                return new_queues

    return new_queues


@ use_browser
def check_color(
    browser: client, village: int, color: str, building_status, queues: list
) -> list:
    new_queues = []
    # notepad = browser.find('//a[@id="notepadButton"]')
    if "possible" in color:  # green
        browser.click_v2(building_status, village)
        browser.hover(notepad, 1)
        log("upgrading..")
        new_queues = queues[1:]
        return new_queues

    if "notNow" in color:  # green / yellow
        construct_slot, queue_slot = check_building_queue(browser, village)
        if queue_slot:
            browser.click_v2(building_status, 1)
            browser.hover(notepad, 1)
            log("queue building..")
            new_queues = queues[1:]
            return new_queues
        else:
            return queues

    if "notAtAll" in color:  # grey
        log("grey, removing from queue.")
        new_queues = queues[1:]
        return new_queues

    if "maxLevel" in color:  # blue
        log("blue, removing from queue.")
        new_queues = queues[1:]
        return new_queues

    return new_queues


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
