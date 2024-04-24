import discord
import re

file_path = "vc_channels.json"
config_path = "config/config.json"
blacklist_path = "blacklist.json"
bot = discord.Bot()
voice_channel_owners = []
config = []
blacklist = []

