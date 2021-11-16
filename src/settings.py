import os
from chromedriver_py import binary_path


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class settings:
    chromedriver_path: str = binary_path
    current_session_path: str = os.path.join(BASE_DIR, "assets", "current_session.txt")
    credentials_path: str = os.path.join(BASE_DIR, "assets", "credentials.txt")
    farmlist_path: str = os.path.join(BASE_DIR, "assets", "farmlist.txt")
    units_path: str = os.path.join(BASE_DIR, "assets", "units.json")
    buildings_path: str = os.path.join(BASE_DIR, "assets", "buildings.json")
    browser_speed: float = 1
