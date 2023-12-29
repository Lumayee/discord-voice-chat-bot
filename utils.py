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


def check_temporary_owner(user):
    # Check if the User owns a temporary VC
    owns_temporary_vc = False
    voice_channel = None

    for item in config.voice_channel_owners:
        if user.id == item.get("User_ID") and item.get("Temp_VC") == "True":
            owns_temporary_vc = True
            vc_id = item.get("VC_Channel_ID")

            voice_channel = get_vc_from_id(vc_id)
            break

    return owns_temporary_vc, voice_channel


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


def get_admin_rights(user):
    # Check if the User has a Moderator Role
    admin_rights = False
    for role in user.roles:
        if role.id in config.config.get("ADMIN_ROLES"):
            admin_rights = True
            break
    return admin_rights


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


def get_temporary_vc_list():
    vc_list = []
    for item in config.voice_channel_owners:
        if item.get("Temp_VC") == "True":
            vc_list.append(item.get("VC_Channel_ID"))
    return vc_list


# Check for inactive VCs
async def check_inactive_vcs():
    while True:
        one_month_seconds = 30 * 24 * 60 * 60  # 30 days in seconds

        for item in config.voice_channel_owners:
            if (item.get("Temp_VC") == "False" and
                    (datetime.now().timestamp() - item.get("Last_Join", 0) > one_month_seconds)):

                vc_channel_id = get_vc_from_id(item.get("VC_Channel_ID"))
                await vc_channel_id.delete()
                await log("Inactive VC: deleted VC with ID: " + str(item.get("VC_Channel_ID")))

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
        await log(ctx.author.mention + " banned " + user.mention + " from " + voice_channel.name)


async def kick_user_from_vc(ctx, voice_channel, user):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights:
        for member in voice_channel.members:
            if member.id == int(user.id):
                await member.move_to(None)
                await log(ctx.author.mention + " kicked " + user.mention + " from " + voice_channel.name)


async def unban_user_from_vc(ctx, voice_channel, user):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights:
        if await remove_ban(user, voice_channel):
            await ctx.respond(f"Banned user from VC", ephemeral=True)
            await log(ctx.author.mention + " unbanned " + user.mention + " from " + voice_channel.name)
        else:
            await ctx.respond(f"Error: Could not ban user", ephemeral=True)


async def rename_vc(ctx, voice_channel, new_name):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights:
        await ctx.respond(f"Changed permanent VC Name to {new_name}", ephemeral=True)
        await log(ctx.author.mention + " changed permanent voice channel name from " + voice_channel.name
                  + " to " + new_name)
        await voice_channel.edit(name=new_name)


async def delete_vc(ctx, voice_channel):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights:
        await voice_channel.delete()
        await ctx.respond(f"Deleted the voice channel", ephemeral=True)
        await log(ctx.author.mention + " deleted permanent voice channel " + voice_channel.name)


async def set_user_count_vc(ctx, voice_channel, user_count):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights:
        if user_count <= 0:
            await voice_channel.edit(user_limit=0)
            await ctx.respond(f"Removed permanent voice chanel user limit", ephemeral=True)
            await log(ctx.author.mention + " removed permanent voice channel user limit from " + voice_channel.name)
        if user_count > 99:
            await voice_channel.edit(user_limit=99)
            await ctx.respond(f"User limit can't be higher than 99, applied 99 as current limit",
                              ephemeral=True)
            await log(ctx.author.mention + " changed permanent voice channel user limit to 99 from "
                      + voice_channel.name)
        else:
            await voice_channel.edit(user_limit=user_count)
            await ctx.respond(f"Changed permanent voice channel User Count", ephemeral=True)
            await log(ctx.author.mention + f" changed permanent voice channel user limit to {user_count} from "
                      + voice_channel.name)


async def check_permissions(ctx, voice_channel):
    if voice_channel is None:
        # Check for Perm User rights
        owns_permanent_vc, voice_channel = check_permanent_owner(ctx.author)
        owns_temporary_vc, voice_channel = check_temporary_owner(ctx.author)

        if owns_permanent_vc and isinstance(voice_channel, discord.VoiceChannel):
            return owns_permanent_vc, voice_channel
        elif owns_temporary_vc and isinstance(voice_channel, discord.VoiceChannel):
            return owns_temporary_vc, voice_channel
        else:
            await ctx.respond(f"You don't own an permanent Voice Channel", ephemeral=True)
            await log(ctx.author.mention + " tried to change a permanent voice channel without owning one")
            return False, None
    else:
        # Check for Mod rights
        mod_rights = get_mod_rights(ctx.author)
        if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
            return mod_rights, voice_channel
        else:
            await ctx.respond(f"You don't have Mod rights", ephemeral=True)
            await log(ctx.author.mention + " tried to change a permanent voice channel without mod rights")
            return False, None


async def log(message):
    print(message)
    channel = discord.utils.get(config.bot.get_all_channels(),
                                id=config.config.get("LOG_CHANNEL"),
                                type=discord.ChannelType.text)

    embed = discord.Embed(title="Test", description="", color=0x00ff00)
    embed.add_field(name="", value=message)

    await channel.send(embed=embed)


async def add_to_list(changing_list, entry):
    changing_list.append(entry)
    with open(config.config_path, "w") as json_file:
        json.dump(config.config, json_file, indent=4)
    json_file.close()


async def remove_from_list(changing_list, entry):
    changing_list.remove(entry)
    with open(config.config_path, "w") as json_file:
        json.dump(config.config, json_file, indent=4)
    json_file.close()
