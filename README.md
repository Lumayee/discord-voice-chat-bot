# Features / Todo List

## Normal User Features
- [x] Create a temporary Voice Chat Channel

## Permanent Voice Chat Channel Features for Special Roles
- [x] Create a permanent Voice Chat Channel
- [x] Set the name of your permanent Voice Chat Channel 
- [x] Set the user count of your permanent Voice Chat Channel
- [x] Delete your permanent Voice Chat Channel
- [x] Kick or Ban a User from your permanent Voice Chat Channel 

## Mod Features
- [x] Delete a permanent Voice Chat Channel
- [x] Rename a permanent Voice Chat Channel
- [x] Kick or Ban a User from a permanent Voice Chat Channel
- [x] Kick a User from a temporary Voice Chat Channel

## Admin Features
- [x] Command to add or remove permanent Roles

## Other Features
- [x] Ping Command
- [x] Help Command
- [x] List permanent Voice Chat roles
- [x] Blacklist for Channel Names
- [x] File to permanently store Channel Information (for all permanent and temporary Voice Chat Channels)



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

- [py-cord](https://docs.pycord.dev/en/stable/index.html)


## config.py

This Bot needs a `config.js`, the file looks like this:

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


## Setup stuff

### Setting up the Python environment and installing the packages

```bash
sudo dnf install python3.11 python3-pip
python3.11 -m venv venv
source venv/bin/activate
pip3 install py-cord
deactivate
```

### Setting up the systemd service

If you want to run the Bot as a service, you can use this example service file:

Create the file `/etc/systemd/system/discord-vc-bot.service` with the following content:

```bash
[Unit]
Description=Discord Voice Channel Bot
After=network.target
Wants=network-online.target

[Service]
User=discord-bots
WorkingDirectory=/srv/discord-bots/discord-voice-chat-bot
ExecStart=/srv/discord-bots/discord-voice-chat-bot/venv/bin/python3.11 /srv/discord-bots/discord-voice-chat-bot/main.py
Restart=always
RestartSec=120

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable discord-vc-bot
sudo systemctl start discord-vc-bot
```


