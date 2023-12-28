import config
import json
import discord
import asyncio
from datetime import datetime


def check_permanent_owner(user):
    # Check if the User owns a permanent VC
    owns_permanent_vc = False
    voice_channel = None

    for item in config.voice_channel_owners:
        if user.id == item.get("User_ID") and item.get("Temp_VC") == "False":
            owns_permanent_vc = True
            vc_id = item.get("VC_Channel_ID")

            voice_channel = get_vc_from_id(vc_id)
            break

    return owns_permanent_vc, voice_channel


def get_user_from_id(user_id):
    for member in config.bot.get_all_members():
        if member.id == int(user_id):
            user = discord.utils.get(config.bot.get_all_members(), id=int(user_id))
            return user
    return None


def get_vc_from_id(vc_id):
    vc_channel_id = discord.utils.get(config.bot.get_all_channels(),
                                      id=int(vc_id),
                                      type=discord.ChannelType.voice)
    return vc_channel_id


def get_mod_rights(user):
    # Check if the User has a Moderator Role
    mod_rights = False
    for role in user.roles:
        if role.id in config.config.get("MOD_ROLES"):
            mod_rights = True
            break
    return mod_rights


async def add_ban(user, voice_channel):
    for item in config.voice_channel_owners:
        if voice_channel.id == item.get("VC_Channel_ID"):
            overwrite = voice_channel.overwrites_for(user)
            overwrite.connect = False
            await voice_channel.set_permissions(user, overwrite=overwrite)

            return True
    return False


async def remove_ban(user, voice_channel):
    for item in config.voice_channel_owners:
        if voice_channel.id == item.get("VC_Channel_ID"):
            overwrite = voice_channel.overwrites_for(user)
            overwrite.connect = True
            await voice_channel.set_permissions(user, overwrite=overwrite)

            return True
    return False


def get_permanent_vc_list():
    vc_list = []
    for item in config.voice_channel_owners:
        if item.get("Temp_VC") == "False":
            vc_list.append(item.get("VC_Channel_ID"))
    return vc_list


# Check for inactive VCs
async def check_inactive_vcs():
    while True:
        print("Checking inactive VCs")
        one_month_seconds = 30 * 24 * 60 * 60  # 30 days in seconds

        for item in config.voice_channel_owners:
            if (item.get("Temp_VC") == "False" and
                    (datetime.now().timestamp() - item.get("Last_Join", 0) > one_month_seconds)):

                vc_channel_id = get_vc_from_id(item.get("VC_Channel_ID"))
                await vc_channel_id.delete()

        await asyncio.sleep(86400)  # 24 hours in seconds


def append_to_json(entry):
    config.voice_channel_owners.append(entry)
    with open(config.file_path, "w") as json_file:
        json.dump(config.voice_channel_owners, json_file, indent=4)
    json_file.close()


async def ban_user_from_vc(ctx, voice_channel, user):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights:
        if await add_ban(user, voice_channel):
            await ctx.respond(f"Banned user from VC", ephemeral=True)
        else:
            await ctx.respond(f"Error: Could not ban user", ephemeral=True)


async def kick_user_from_vc(ctx, voice_channel, user):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights:
        for member in voice_channel.members:
            if member.id == int(user.id):
                await member.move_to(None)


async def unban_user_from_vc(ctx, voice_channel, user):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights:
        if await remove_ban(user, voice_channel):
            await ctx.respond(f"Banned user from VC", ephemeral=True)
        else:
            await ctx.respond(f"Error: Could not ban user", ephemeral=True)


async def rename_vc(ctx, voice_channel, new_name):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights:
        await voice_channel.edit(name=new_name)
        await ctx.respond(f"Changed permanent VC Name to {new_name}", ephemeral=True)


async def delete_vc(ctx, voice_channel):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights:
        await voice_channel.delete()
        await ctx.respond(f"Deleted the voice channel", ephemeral=True)


async def set_user_count_vc(ctx, voice_channel, user_count):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights:
        if user_count == 0:
            await voice_channel.edit(user_limit=0)
            await ctx.respond(f"Removed permanent VC User Limit", ephemeral=True)
        if user_count > 99:
            await voice_channel.edit(user_limit=99)
            await ctx.respond(f"User count can't be higher than 99, applied 99 as current limit",
                              ephemeral=True)
        else:
            await voice_channel.edit(user_limit=user_count)
            await ctx.respond(f"Changed permanent VC User Count", ephemeral=True)


async def check_permissions(ctx, voice_channel):
    if voice_channel is None:
        # Check for Perm User rights
        owns_permanent_vc, voice_channel = check_permanent_owner(ctx.author)
        if owns_permanent_vc and isinstance(voice_channel, discord.VoiceChannel):
            return owns_permanent_vc, voice_channel
        else:
            await ctx.respond(f"You don't own a permanent VC", ephemeral=True)
            return False, None
    else:
        # Check for Mod rights
        mod_rights = get_mod_rights(ctx.author)
        if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
            return mod_rights, voice_channel
        else:
            await ctx.respond(f"You don't have Mod rights", ephemeral=True)
            return False, None
