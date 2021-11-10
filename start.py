from src import king_bot, settings
import sys

# these could be read in via arguments, file or login manually - read documentation
gameworld = "FR1X3"  # choose uppercase (exact world name) - optional
email = "turbo"  # optional
password = "turbo"  # optional
proxy = ""  # optional
# increase the number if your internet connecion is slow
settings.browser_speed = 0.5


kingbot = king_bot(
    email=email,
    password=password,
    gameworld=gameworld,
    proxy=proxy,
    start_args=sys.argv,
    debug=True,
)

# place your actions below
# kingbot.start_adventures(1000)
# kingbot.upgrade_units_smithy(village=0, units=[2, 5])

kingbot.start_building(village= 1, file_name="village_2.json" , interval=30)

# kingbot.dodge_attack(
#     village=0,
#     interval=300,
#     save_resources=False,
#     units=[3, 4],
#     target=[4, 27],
#     units_train=[1],
# )
# kingbot.robber_hideout(village=0, interval=600, units={4: 100, 10: -1})
# kingbot.train_troops(village=0, units=[1])
# kingbot.robber_camp(village=0, interval=600, units={4: 100, 10: -1})
