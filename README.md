# Discord Bot to manage Voice Chat Channels

This Bot is used to create and delete Voice Channels. The main function is to create new temporary Voice Chat Channels when a user joins a `Join to create new VC` Channel.
The user that joined the creation VC will have all rights for the new Channel, when a channel is empty, it will be deleted.

In contrast to temporary, the Bot can also create permanent Channels, these will be created with `/vc_create`. 
A user has to have a specific Role to create these VCs and each User can only create one permanent Channel.
Like the temporary Channels the User that ran the command will have all the Channel rights.

## Requirements

This bot needs `py-chord`

```bash
python3 -m pip install -U py-cord
```

## Commands

- `/vc_create` - creates a permanent Voice Chat Channel 
- `/ping` - get the Latency of the Bot

## config.py

This Bot needs a `config.js`, the file looks like this:

```py
TOKEN = 'string'
CREATE_CHANNEL = int
VC_CATEGORY = int
PERMANENT_ROLES = [int, int] or int
```

- `TOKEN` has to be your Bot Token, keep in Mind, that this has to be in `''` becuase it will be used as a string.
- `CREATE_CHANNEL` is the ID of the Voice Chat Channel, that people can join to create new temporary ones.
- `VC_CATEGORY` is the is the category in which the permanent Voice Channels will be created.
- `PERMANENT_ROLES` one or more Role IDs that can create permanent Voice Channels

# Features
- Create temp Voice Channel
- Create permanent Voice Channel with `/vc_create` (only for permanent Voice Channels)
- Rename permanent Voice Channel with `/vc_set_name` (only for permanent Voice Channels)
- Set User Count with `/vc_set_user_count` 0 is unlimited (only for permanent Voice Channels)
- Delete permanent Voice Channel with `/vc_delete` (only for permanent Voice Channels)


# Setup stuff

```bash
sudo dnf install python3.11 python3-pip
python3.11 -m venv PM-VC
source PM-VC/bin/activate
pip3 install py-cord
deactivate
```

/etc/systemd/system/Discord-VC-Bot.service

```bash
[Unit]
Description=Discord Voice Channel Bot
After=network.target

[Service]
User=potion-maker-bots
WorkingDirectory=/home/potion-maker-bots/VC-Bot
ExecStart=/home/potion-maker-bots/VC-Bot/PM-VC/bin/python3.11 /home/potion-maker-bots/VC-Bot/main.py

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable Discord-VC-Bot
sudo systemctl start Discord-VC-Bot
```


