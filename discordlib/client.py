import json
from discord import Intents
from discord.ext import commands

def build_bot_from_config(config):
    new_config = {}

    def get_prefix(bot,msg):
        prefixes = config.get('prefixes')
        if prefixes:
            if "{{when_mentioned}}" in prefixes:
                return commands.when_mentioned_or(*(set(prefixes) - {"{{when_mentioned}}"}))(bot,msg)
            else:
                return prefixes
        else:
            return commands.when_mentioned(bot,msg)

    new_config['command_prefix'] = get_prefix
    new_config['owner_id'] = config.get('owner')
    new_config['description'] = config.get('description')
    new_config['case_insensitive'] = not config.get('case_sensitive', True)
    new_config['intents'] = Intents.all() if config.get('intents') == 'all' else Intents.default()
    
    return commands.Bot(**new_config)

class Client:
    def __init__(self, bot_data):
        self.bot_data = bot_data
        self.config = self.bot_data.get("config")
        self.bot = build_bot_from_config(self.config)

    def run(self):
        self.bot.run(self.config["token"])
