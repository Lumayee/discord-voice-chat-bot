import config
import json
import discord
import asyncio
from datetime import datetime

def check_permanent_owner(user_id):
    # Check if the User owns a permanent VC
    owns_permanent_vc = False
    voice_channel = None

    for item in config.voice_channel_owners:
        if user_id == item.get("User_ID") and item.get("Temp_VC") == "False":
            owns_permanent_vc = True
            vc_id = item.get("VC_Channel_ID")

            voice_channel = discord.utils.get(config.bot.get_all_channels(),
                                              id=int(vc_id),
                                              type=discord.ChannelType.voice)
            break

    return owns_permanent_vc, voice_channel


def getUserFromID(user_id):
    for member in config.bot.get_all_members():
        if member.id == int(user_id):
            user = discord.utils.get(config.bot.get_all_members(), id=int(user_id))
            return user
    return None


def getVCFromID(vc_id):
    vc_channel_id = discord.utils.get(config.bot.get_all_channels(),
                                      id=int(vc_id),
                                      type=discord.ChannelType.voice)
    return vc_channel_id


def getModRights(user_id):
    # Check if the User has a Moderator Role
    mod_rights = False
    for role in user_id.roles:
        if role.id in config.MOD_ROLES:
            mod_rights = True
            break
    return mod_rights


def isUserBanned(user_id, vc_id):
    for item in config.voice_channel_owners:
        if vc_id == item.get("VC_Channel_ID"):
            if user_id in item.get("Ban"):
                return True
    return False


def getBanList(vc_id):
    for item in config.voice_channel_owners:
        if vc_id == item.get("VC_Channel_ID"):
            return item.get("Ban")
    return None


def addBan(user_id, vc_id):
    for item in config.voice_channel_owners:
        if vc_id == item.get("VC_Channel_ID"):
            item.get("Ban").append(user_id)
            with open(config.file_path, "w") as json_file:
                json.dump(config.voice_channel_owners, json_file, indent=4)
            return True
    return False


def removeBan(user_id, vc_id):
    for item in config.voice_channel_owners:
        if vc_id == item.get("VC_Channel_ID"):
            item.get("Ban").remove(user_id)
            with open(config.file_path, "w") as json_file:
                json.dump(config.voice_channel_owners, json_file, indent=4)
            return True
    return False


def isBanned(user_id, vc_id):
    for item in config.voice_channel_owners:
        for ban in item.get("Ban"):
            if user_id == int(ban) and vc_id == item.get("VC_Channel_ID"):
                return True
    return False


def getPermaentVCIDList():
    test = []
    for item in config.voice_channel_owners:
        if item.get("Temp_VC") == "False":
            test.append(item.get("VC_Channel_ID"))
    return test


# Check for inactive VCs
async def check_inactive_vcs():
    while True:
        print("Checking inactive VCs")
        one_month_seconds = 30 * 24 * 60 * 60  # 30 days in seconds

        for item in config.voice_channel_owners:
            if (item.get("Temp_VC") == "False" and
                    (datetime.now().timestamp() - item.get("Last_Join", 0) > one_month_seconds)):
                vc_channel_id = discord.utils.get(config.bot.get_all_channels(),
                                                  id=int(item["VC_Channel_ID"]),
                                                  type=discord.ChannelType.voice)
                await vc_channel_id.delete()

        await asyncio.sleep(86400)  # 24 hours in seconds


async def kick_user_from_vc(voice_channel, user_id):
    if isinstance(voice_channel, discord.VoiceChannel):
        for member in voice_channel.members:
            if member.id == int(user_id):
                await member.move_to(None)
                return True
        return False


def append_to_json(entry):
    config.voice_channel_owners.append(entry)
    with open(config.file_path, "w") as json_file:
        json.dump(entry, json_file, indent=4)
    json_file.close()