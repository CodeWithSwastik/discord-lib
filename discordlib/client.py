import os
from typing import Dict, List

from discord import (
    Intents,
    Game,
    Activity,
    Streaming,
    ActivityType,
    AllowedMentions,
    Embed,
)
from discord.ext.commands import (
    Bot,
    Command,
    Context,
    Cog,
    when_mentioned,
    when_mentioned_or,
)

from .action import Action
from .utils import apply_func_to_all_strings, spformat, change_case_for_dict_keys

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
    presence_data = config.get("presence") or config.get("activity")
    if presence_data:
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

    allowed_input = config.get("allowed_mentions")
    if allowed_input:
        allowed = AllowedMentions.none()

        if isinstance(allowed_input, str):
            if allowed_input == "all":
                allowed = AllowedMentions.all()
        else:
            for f in allowed_input:
                setattr(allowed, f, True)
        new_config["allowed_mentions"] = allowed

    bot = Bot(**new_config)

    if "jishaku" in config.get("include", []):
        try:
            bot.load_extension("jishaku")
        except Exception:
            raise ModuleNotFoundError(
                "Unable to use jishaku. "
                "jishaku is required if you want to include it, install using\n"
                "pip install jishaku"
            )

    return bot

def add_cogs(bot: Bot, cog_configs: List[Dict]):
    for cog_config in cog_configs:
        bot.add_cog(create_cog(cog_config, bot))

def create_cog(cog_config, bot) -> Cog:
    
    cog = Cog(name=cog_config['config']['name'], description=cog_config['config'].get('description',''))
    add_commands(bot, cog_config.get('commands',cog_config.get('command',[])), cog)
    #add_listeners(bot, cog_config.get('events',cog_config.get('event',[])), cog)
    return cog

def add_commands(bot: Bot, command_configs: List[Dict], cog = None):
    for command_config in command_configs:
        bot.add_command(create_command(command_config,cog))


def create_command(command_config: Dict, cog) -> Command:
    defined_args = command_config.get("args", [])
    async def command(ctx: Context, *args):
        for i, arg in enumerate(defined_args):
            if arg.startswith("*"):
                setattr(ctx, arg[1:], " ".join(args[i:]))
                break
            setattr(ctx, arg, args[i])
        def fill(string):
            return spformat(string, ctx)
        local_command_config = apply_func_to_all_strings(command_config, fill)
        action = local_command_config.get("action")
        if action:
            Action(action, namespace=ctx).execute()
        local_command_config = apply_func_to_all_strings(command_config, fill)

        resp = local_command_config.get("response")
        if resp:
            await ctx.send(fill(resp))
        rep = local_command_config.get("reply")
        if rep:
            await ctx.reply(fill(rep))
        embed = local_command_config.get("embed")
        if embed:
            final_embed = Embed.from_dict(embed)
            await ctx.send(embed=final_embed)

    aliases = command_config.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]

    return Command(
        command,
        name=command_config["name"],
        aliases=aliases,
        description=command_config.get("description", ""),
        cog=cog
    )


def add_listeners(bot: Bot, event_configs: List[Dict]):
    for event_config in event_configs:
        bot.add_listener(*create_event(event_config))


def create_event(event_config: Dict):
    async def event(*args, **kwargs):
        action = event_config.get("action")
        if action:
            Action(action).execute()

    return (event, event_config["name"])


class Client:
    def __init__(self, bot_data):
        if isinstance(bot_data, str):
            self.bot_data = self.load(bot_data)
        else:
            self.bot_data = bot_data
        self.config = self.bot_data.get("config")
        self.commands = self.bot_data.get("commands") or self.bot_data.get(
            "command", []
        )
        self.events = self.bot_data.get("events") or self.bot_data.get("event", [])
        self.bot = build_bot_from_config(self.config)
        add_commands(self.bot, self.commands)
        add_listeners(self.bot, self.events)
        self.load_extensions()

    def run(self):
        if self.config["token"] == "{{env.token}}":
            try:
                from dotenv import load_dotenv
            except ImportError:
                raise ModuleNotFoundError(
                    "Unable to import dotenv. "
                    "dotenv is required for using env files, install using\n"
                    "pip install python-dotenv"
                )
            else:
                load_dotenv(dotenv_path=os.path.join(os.getcwd(),".env"))
            self.config["token"] = os.getenv("TOKEN") or os.getenv("token")

        self.bot.run(self.config["token"])

    def load(self,fp) -> Dict:
        with open(fp, "rb") as f:
            _, filetype = os.path.splitext(fp)
            self.filetype = filetype
            if filetype == ".json":
                import json

                result = json.load(f)
            elif filetype == ".xml":
                from .utils import parse_xml_to_dict

                result = parse_xml_to_dict(f)
            elif filetype in (".yaml", ".yml"):
                try:
                    import yaml
                except ModuleNotFoundError:
                    raise ModuleNotFoundError(
                        "Unable to import yaml. "
                        "xmltodict is required for using yaml files, install using\n"
                        "pip install PyYAML"
                    )
                result = yaml.safe_load(f)
            else:
                raise Exception("Unsupported filetype")

        return change_case_for_dict_keys(result)

    def load_extensions(self):
        cogs = self.config.get("cogs")
        self.cog_configs = []
        if isinstance(cogs,str):
            cog_path = os.path.join(os.getcwd(), cogs)
            for cog in os.listdir(cog_path):
                if self.filetype == os.path.splitext(cog)[-1]:
                    cog_config = self.load(os.path.join(cog_path, cog))
                    if cog_config.get('config',{}).get('type', '') != 'cog':
                        raise Exception(f"{cog} doesn't specify a type. In order to load it as a cog, specify type: cog")
                    self.cog_configs.append(cog_config)
        elif isinstance(cogs,list):
            for cog in cogs:
                if self.filetype == os.path.splitext(cog)[-1]:
                    cog_config = self.load(cog)
                    if cog_config.get('config',{}).get('type', '') != 'cog':
                        raise Exception(f"{cog} doesn't specify a type. In order to load it as a cog, specify type: cog")                    
                    self.cog_configs.append(cog_config)

        add_cogs(self.bot,self.cog_configs)
