import json
from discordlib import Client

with open("tests/bot.json", "r") as f:
    bot = Client(json.load(f))

bot.run()
