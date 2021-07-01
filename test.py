import json
from discordlib.client import Client

with open("tests/bot.json", "r") as f:
    bot = Client(json.load(f))

bot.run()
