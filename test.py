import json
from discordlib import Client

# with open("tests/bot.json", "r") as f:
#     bot = Client(json.load(f))

# bot.run()

import xmltodict
from discordlib.utils import *

with open("tests/bot.xml", "rb") as f:
    bot = Client(parse_xml_to_dict(f))
bot.run()