import json

from discord import Intents
from discord.ext import commands


def build_bot_from_config(config):
    new_config = {}

    def get_prefix(bot, msg):
        prefixes = config.get("prefixes")
        if prefixes:
            if "{{when_mentioned}}" in prefixes:
                return commands.when_mentioned_or(
                    *(set(prefixes) - {"{{when_mentioned}}"})
                )(bot, msg)
            else:
                return prefixes
        else:
            return commands.when_mentioned(bot, msg)

    new_config["command_prefix"] = get_prefix
    new_config["owner_id"] = config.get("owner")
    new_config["description"] = config.get("description")
    new_config["case_insensitive"] = not config.get("case_sensitive", True)
    new_config["intents"] = (
        Intents.all() if config.get("intents") == "all" else Intents.default()
    )

    return commands.Bot(**new_config)


class Client:
    def __init__(self, bot_data):
        self.bot_data = bot_data
        self.config = self.bot_data.get("config")
        self.bot = build_bot_from_config(self.config)
        add_commands(self.bot, bot_data["commands"])

    def run(self):
        self.bot.run(self.config["token"])


import re
from typing import Dict, List

from discord.ext.commands import Bot, Command, Context

matcher = re.compile(r"(?:\{\{)([a-zA-Z\.]+)(?:\}\})")
replacer = "{0.\\1}"


def add_commands(bot: Bot, command_configs: List[Dict]):
    for command_config in command_configs:
        bot.add_command(create_command(command_config))


def create_command(command_config: Dict) -> Command:
    response = matcher.sub(replacer, command_config["response"])

    async def command(ctx: Context):
        await ctx.send(response.format(ctx))

    return Command(
        command, name=command_config["name"], aliases=command_config.get("aliases", [])
    )
