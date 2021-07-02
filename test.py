# import xmltodict
# 

# with open("tests/bot.xml", "rb") as f:
#     print(json.loads(json.dumps(xmltodict.parse(f))))

# quit()
import json
from discordlib import Client

with open("tests/bot.json", "r") as f:
    bot = Client(json.load(f))

bot.run()
