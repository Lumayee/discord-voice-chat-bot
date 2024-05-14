
# Commands

- `/vc_create` - creates a permanent Voice Chat Channel 
- `/ping` - get the Latency of the Bot
- `/vc_rename` - set the name of a permanent Voice Chat Channel
- `/vc_set_user_count` - set the user count of a permanent Voice Chat Channel
- `/vc_delete` - delete a permanent Voice Chat Channel
- `/vc_mod_delete` - delete a permanent Voice Chat Channel (only for Mods)
- `/vc_mod_rename` - set the name of a permanent Voice Chat Channel (only for Mods)

# If you want to use this Bot yourself

## Requirements

- Docker 

## Usage

docker-compose.yaml
```yaml
services:
  discord-vc-bot:
    image: lumaye/discord-vc-bot:0.1
    restart: unless-stopped
    container_name: discord-vc-bot
    volumes:
      - ./vc-config/:/app/config
```

You have to put your config.json in the config folder.

## config.json

This Bot needs a `config.json`, the file looks like this:

```py
TOKEN = 'string'
CREATE_CHANNEL = int
VC_CATEGORY = int
PERMANENT_ROLES = [int, int] or int
MOD_ROLES = [int, int] or int
```

- `TOKEN` has to be your Bot Token, keep in Mind, that this has to be in `''` because it will be used as a string.
- `CREATE_CHANNEL` is the ID of the Voice Chat Channel, that people can join to create new temporary ones.
- `VC_CATEGORY` is the is the category in which the permanent Voice Channels will be created.
- `PERMANENT_ROLES` one or more Role IDs that can create permanent Voice Channels
- `MOD_ROLES` one or more Role IDs that can use the Mod Bot Commands

# Work on the Code
I'm using [py-cord](https://docs.pycord.dev/en/stable/index.html) for this bot, if you want to work on the code you have to install it.

If you want to create the container image yourself `docker build -t x/discord-vc-bot .`



