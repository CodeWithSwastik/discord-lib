import re
from typing import Dict, List

from discord import Intents, Game, Activity, Streaming, ActivityType
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
        prefixes = config.get("prefix") or config.get("prefixes")
        if not isinstance(prefixes, list):
            prefixes = [prefixes]
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
    if presence_data := (config.get("presence") or config.get("activity")):
        presence_type = presence_data.get("type", "playing")
        text = presence_data.get("text")

        if presence_type == "watching":
            activity = Activity(type=ActivityType.watching, name=text)
        elif presence_type == "listening":
            activity = Activity(type=ActivityType.listening, name=text)
        elif presence_type == "streaming":
            activity = Streaming(name=text, url=presence_data.get("url"))
        else:
            activity = Game(name=text)
        new_config["activity"] = activity
    return Bot(**new_config)


matcher = re.compile(r"(?:\{\{)([a-zA-Z\.]+)(?:\}\})")
replacer = "{0.\\1}"


def add_commands(bot: Bot, command_configs: List[Dict]):
    for command_config in command_configs:
        bot.add_command(create_command(command_config))


def create_command(command_config: Dict) -> Command:
    async def command(ctx: Context):

        if command_config.get("response"):
            response = matcher.sub(replacer, command_config["response"])
            await ctx.send(response.format(ctx))
        if command_config.get("reply"):
            reply = matcher.sub(replacer, command_config.get("reply"))
            await ctx.reply(reply.format(ctx))

    return Command(
        command, name=command_config["name"], aliases=command_config.get("aliases", [])
    )


def add_listeners(bot: Bot, event_configs: List[Dict]):
    for event_config in event_configs:
        bot.add_listener(*create_event(event_config))


def create_event(event_config: Dict):
    async def event(*args, **kwargs):
        if action := event_config.get("action"):
            if action["type"] == "log":
                print(action["value"])

    return (event, event_config["name"])


class Client:
    def __init__(self, bot_data: Dict):
        self.bot_data = bot_data
        self.config = self.bot_data.get("config")
        self.commands = self.bot_data.get("commands")
        self.events = self.bot_data.get("events")
        self.bot = build_bot_from_config(self.config)
        add_commands(self.bot, self.commands)
        add_listeners(self.bot, self.events)

    def run(self):
        self.bot.run(self.config["token"])
