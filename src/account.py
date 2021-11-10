from .utils import log
from .custom_driver import client, use_browser


@use_browser
def login(browser: client, gameworld: str, email: str, password: str) -> None:
    world = gameworld

    browser.get("https://qtatar.com/join?s=1")

     
    
    browser.find("//input[@name='name']").send_keys(email)
    pw = browser.find("//input[@name='password']").send_keys(password)
    browser.find("//button[@name='submit']").click()
    #  check_notification(browser)

    # # login to gameworld
    # browser.find(
    #     "//span[contains(text(), '{}')]/following::button[@type='button']".format(world)
    # ).click()

    log("login successful")
    # browser.sleep(3)


def check_notification(browser: client) -> None:
    try:
        browser.find("//body[contains(@class, 'modal-open')]")
        log("closing notification-modal")
        btn_close = browser.find("//button[@class='close']")
        browser.click(btn_close, 1)
    except:
        pass
