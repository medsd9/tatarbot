from .custom_driver import client
from .adventures import adventures_thread
from threading import Thread
import platform
import sys
import getopt
from .account import login
import time
from .util_game import close_welcome_screen
from .utils import log, error, warning
from .farming import (
    start_farming_thread,
    start_custom_farmlist_thread,
    sort_danger_farms_thread,
)
from .dodge_attack import check_for_attack_thread
from .upgrade import upgrade_units_smithy_thread
from .settings import settings
from .celebration import celebration_thread
from .master_builders import master_builder_thread
from .robber_hideouts import robber_hideout_thread
from .train_troops import train_troops_thread
from .robber_camps import robber_camp_thread


class king_bot:
    def __init__(
        self,
        email: str,
        password: str,
        gameworld: str,
        proxy: str,
        start_args: list,
        debug: bool = False,
    ) -> None:
        self.browser = client(debug=debug)
        self.chrome_driver_path = settings.chromedriver_path
        self.gameworld = gameworld

        self.init(email=email, password=password, proxy=proxy, start_args=start_args)

    def init(self, email: str, password: str, proxy: str, start_args: list) -> None:
        # print("This Bot does not work anymore!")
        # print("Travian will detect the Bot and Ban your Account if you still try to run it.")
        # sys.exit(0)

        login_req = True
        login_sleeptime = 0
        manual_login = False

        try:
            opts, _ = getopt.getopt(
                start_args[1:], "htrm:e:p:w:", ["email=", "password=", "gameworld="]
            )
        except:
            print("error in arguments. check github for details.")
            sys.exit()
        for opt, arg in opts:
            if opt == "-t":
                # todo run units tests
                # checks dependencies for travis
                print("all imports resolved")
                sys.exit()
            elif opt == "-h":
                self.browser.headless(self.chrome_driver_path, proxy=proxy)
            elif opt == "-r":
                self.browser.remote()
                login_req = False
            elif opt == "-m":
                login_req = False
                manual_login = True
                login_sleeptime = int(arg)
            elif opt in ("-e", "--email"):
                email = arg
            elif opt in ("-p", "--password"):
                password = arg
            elif opt in ("-w", "--gameworld"):
                self.gameworld = arg

        if self.browser.driver is None:
            self.browser.chrome(self.chrome_driver_path, proxy=proxy)

        if login_req:
            if not email or not password or not self.gameworld:
                # read login credentials
                file = open(settings.credentials_path, "r")
                lines = file.read().splitlines()
                text = lines[0]
                file.close()

                if not self.gameworld:
                    self.gameworld = text.split(";")[0]
                if not email:
                    email = text.split(";")[1]
                if not password:
                    password = text.split(";")[2]

            close = False
            if not self.gameworld:
                log("no gameworld provided")
                close = True

            if not email:
                log("no email provided")
                close = True

            if not password:
                log("no password provided")
                close = True

            if close:
                sys.exit()

            login(
                browser=self.browser,
                gameworld=self.gameworld,
                email=email,
                password=password,
            )

            # clear loging credentials
            email = ""
            password = ""

        if manual_login:
            self.browser.use()
            self.browser.get("https://kingdoms.com")
            time.sleep(login_sleeptime)
            self.browser.done()

        self.browser.use()

        try:
            close_welcome_screen(self.browser)
        except:
            pass

        self.browser.done()

    def start_adventures(self, interval: int = 100, health: int = 50) -> None:
        Thread(
            target=adventures_thread,
            name="adventures",
            args=[self.browser, interval, health],
        ).start()

    # todo implement
    def upgrade_slot(self, village: int, slot: int) -> None:
        error("upgrading slots is under construction - check for updates")

        if slot > 19:
            error("upgrading buildings is still under construction")
            return

    def start_farming(self, village: int, farmlists: list, interval: int) -> None:
        Thread(
            target=start_farming_thread,
            name="farming",
            args=[self.browser, village, farmlists, interval],
        ).start()

    def start_custom_farmlist(self, reload: bool = False) -> None:
        Thread(
            target=start_custom_farmlist_thread,
            name="custom_farmlist",
            args=[self.browser, reload],
        ).start()

    def sort_danger_farms(
        self,
        farmlists: list,
        to_list: int,
        red: bool,
        yellow: bool,
        interval: int = 300,
    ) -> None:
        Thread(
            target=sort_danger_farms_thread,
            name="sort_danger_farms",
            args=[self.browser, farmlists, to_list, red, yellow, interval],
        ).start()

    def dodge_attack(
        self,
        village: int,
        interval: int = 600,
        save_resources: bool = False,
        units: list = [],
        target: list = [],
        units_train: list = [],
    ) -> None:
        # check dependencies for units
        if units:
            if target == None:
                warning(
                    "dodge_attack: please provide a target to send your troops for saving"
                )
                return

        # check dependencies for resources
        if save_resources:
            if units_train == None:
                warning(
                    "dodge_attack: please provide the units that want to train for saving the resources"
                )
                return

        Thread(
            target=check_for_attack_thread,
            name="dodge_attack",
            args=[
                self.browser,
                village,
                interval,
                units,
                target,
                save_resources,
                units_train,
            ],
        ).start()

    def upgrade_units_smithy(
        self, village: int, units: list, interval: int = 1000
    ) -> None:
        Thread(
            target=upgrade_units_smithy_thread,
            name="upgrade_units_smithy",
            args=[self.browser, village, units, interval],
        ).start()

    def celebrate(self, villages: list, interval: int = 1000) -> None:
        # TODO implement type == 1 for big celebrations
        celebration_type = 0

        Thread(
            target=celebration_thread,
            name="celebrate",
            args=[self.browser, villages, celebration_type, interval],
        ).start()

    def start_building(
        self, village: int, file_name: str, interval: int = 1800
    ) -> None:
        Thread(
            target=master_builder_thread,
            name="building",
            args=[self.browser, village, file_name, interval],
        ).start()

    def robber_hideout(
        self, village: int, units: dict = {}, interval: int = 600
    ) -> None:
        Thread(
            target=robber_hideout_thread,
            name="robber_hideout",
            args=[self.browser, village, units, interval],
        ).start()

    def train_troops(
        self, village: int, units: list = None, interval: int = 600
    ) -> None:
        if units == None:
            warning("train_troops: please provide the units you want to train")
            return
        Thread(
            target=train_troops_thread,
            name="train_troops",
            args=[self.browser, village, units, interval],
        ).start()

    def robber_camp(self, village: int, units: dict = {}, interval: int = 600) -> None:
        Thread(
            target=robber_camp_thread,
            name="robber_camp",
            args=[self.browser, village, units, interval],
        ).start()
