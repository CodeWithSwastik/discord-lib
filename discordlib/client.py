import re
from typing import Dict, List

from discord import Intents, Game, Activity, Streaming, ActivityType, AllowedMentions
from discord.ext.commands import (
    Bot,
    Command,
    Context,
    when_mentioned,
    when_mentioned_or,
)

from .action import Action


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

    if allowed_input := (config.get("allowed_mentions")):
        allowed = AllowedMentions.none()

        if isinstance(allowed_input, str):
            if allowed_input == "all":
                allowed = AllowedMentions.all()
        else:
            for f in allowed_input:
                setattr(allowed, f, True)
        new_config["allowed_mentions"] = allowed
    return Bot(**new_config)


matcher = re.compile(r"(?:\{\{)([a-zA-Z0-9\.]+)(?:\}\})")
replacer = "{0.\\1}"


def add_commands(bot: Bot, command_configs: List[Dict]):
    for command_config in command_configs:
        bot.add_command(create_command(command_config))


def create_command(command_config: Dict) -> Command:
    defined_args = command_config.get("args", [])

    async def command(ctx: Context, *args):
        for i, arg in enumerate(defined_args):
            if arg.startswith("*"):
                setattr(ctx, arg[1:], " ".join(args[i:]))
                break
            setattr(ctx, arg, args[i])

        if action := command_config.get("action"):
            Action(action, namespace=ctx).execute()

        if resp := command_config.get("response"):
            response = matcher.sub(replacer, resp)
            await ctx.send(response.format(ctx))
        if rep := command_config.get("reply"):
            reply = matcher.sub(replacer, rep)
            await ctx.reply(reply.format(ctx))

    aliases = command_config.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]

    return Command(
        command,
        name=command_config["name"],
        aliases=aliases,
        description=command_config.get("description", ""),
    )


def add_listeners(bot: Bot, event_configs: List[Dict]):
    for event_config in event_configs:
        bot.add_listener(*create_event(event_config))


def create_event(event_config: Dict):
    async def event(*args, **kwargs):
        if action := event_config.get("action"):
            Action(action).execute()

    return (event, event_config["name"])


class Client:
    def __init__(self, bot_data: Dict):
        self.bot_data = bot_data
        self.config = self.bot_data.get("config")
        self.commands = self.bot_data.get("commands") or self.bot_data.get(
            "command", []
        )
        self.events = self.bot_data.get("events") or self.bot_data.get("event", [])
        self.bot = build_bot_from_config(self.config)
        add_commands(self.bot, self.commands)
        add_listeners(self.bot, self.events)

    def run(self):
        self.bot.run(self.config["token"])
