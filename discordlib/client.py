import re
from typing import Dict, List

from discord import Intents
from discord.ext.commands import (
    Bot,
    Command,
    Context,
    when_mentioned,
    when_mentioned_or,
)


def build_bot_from_config(config: Dict) -> Bot:
    new_config = {}

    def get_prefix(bot, msg):
        prefixes = config.get("prefixes")
        if prefixes:
            mentioned = "{{when_mentioned}}"
            if mentioned in prefixes:
                return when_mentioned_or(*(set(prefixes) - {mentioned}))(bot, msg)
            else:
                return prefixes
        else:
            return when_mentioned(bot, msg)

    new_config["command_prefix"] = get_prefix
    new_config["owner_id"] = config.get("owner")
    new_config["description"] = config.get("description")
    new_config["case_insensitive"] = not config.get("case_sensitive", True)
    new_config["intents"] = (
        Intents.all() if config.get("intents") == "all" else Intents.default()
    )

    return Bot(**new_config)


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


class Client:
    def __init__(self, bot_data: Dict):
        self.bot_data = bot_data
        self.config = self.bot_data.get("config")
        self.commands = self.bot_data.get("commands")
        self.bot = build_bot_from_config(self.config)
        add_commands(self.bot, self.commands)

    def run(self):
        self.bot.run(self.config["token"])
