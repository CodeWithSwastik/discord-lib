import json
from discordlib.client import build_bot_from_config

with open("tests/bot.json", "r") as f:
    e = json.load(f)
    config = e.get("config")
    bot = build_bot_from_config(config)
    
bot.run(config["token"])