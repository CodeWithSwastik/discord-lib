# discord-lib 0.0.6

discord-lib currently supports discord bots written in JSON, XML and yaml. It will soon support toml, etc

## Installation

```
pip install git+https://github.com/CodeWithSwastik/discord-lib
```

## Usage

### CLI

```
pythom -m discordlib [filepath]
```

### Code

```python
from discordlib import Client

client = Client("filepath")
client.run()
```

Note:
You can access the commands.Bot object by referencing `client.bot` and with it you can manipulate it however you want (add commands, listeners, anything that can be done with discord.py).

## Current Limitations:

- There is no way to extend the namespace outside a command
- There is no way to use a database
- Listeners don't work well
