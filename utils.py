import config
import json
import discord
import asyncio
from datetime import datetime
import re


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
                await log("Inactive VC: deleted VC with ID: " + str(item.get("VC_Channel_ID")),
                          "Check for inactive VCs", "non urgent")

        await asyncio.sleep(86400)  # 24 hours in seconds


def append_to_json(entry):
    config.voice_channel_owners.append(entry)
    with open(config.file_path, "w") as json_file:
        json.dump(config.voice_channel_owners, json_file, indent=4)
    json_file.close()


async def ban_user_from_vc(ctx, voice_channel, user):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights and voice_channel is not None:
        if await add_ban(user, voice_channel):
            await ctx.respond(f"Banned user from VC", ephemeral=True)
        else:
            await ctx.respond(f"Error: Could not ban user", ephemeral=True)
        await log(ctx.author.mention + " banned " + user.mention + " from " + voice_channel.name,
                  "Ban User", "critical")
    else:
        await ctx.respond(f"Something went wrong", ephemeral=True)


async def kick_user_from_vc(ctx, voice_channel, user):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights and voice_channel is not None:
        for member in voice_channel.members:
            if member.id == int(user.id):
                await member.move_to(None)
                await log(ctx.author.mention + " kicked " + user.mention + " from " + voice_channel.name,
                          "Kick User", "normal")
    else:
        await ctx.respond(f"Something went wrong", ephemeral=True)


async def unban_user_from_vc(ctx, voice_channel, user):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights and voice_channel is not None:
        if await remove_ban(user, voice_channel):
            await ctx.respond(f"Unbanned user from VC", ephemeral=True)
            await log(ctx.author.mentioan + " unbanned " + user.mention + " from " + voice_channel.name,
                      "Unban User", "critical")
        else:
            await ctx.respond(f"Error: Could not ban user", ephemeral=True)
    else:
        await ctx.respond(f"Something went wrong", ephemeral=True)


async def rename_vc(ctx, voice_channel, new_name):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights and voice_channel is not None:
        filtered_name = blacklist_filter(new_name, config.blacklist)
        if filtered_name != new_name:
            await ctx.respond(f"The new name contained illegal words", ephemeral=True)
            await log(ctx.author.mention + " used an illegal word in " + new_name,
                      "Rename VC", "critical")

        await ctx.respond(f"Changed permanent VC Name to {filtered_name}", ephemeral=True)
        await log(ctx.author.mention + " changed permanent voice channel name from " + voice_channel.name
                  + " to " + filtered_name, "Rename VC", "normal")
        await voice_channel.edit(name=filtered_name)
    else:
        await ctx.respond(f"Something went wrong", ephemeral=True)


async def delete_vc(ctx, voice_channel):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights and voice_channel is not None:
        await voice_channel.delete()
        await ctx.respond(f"Deleted the voice channel", ephemeral=True)
        await log(ctx.author.mention + " deleted permanent voice channel " + voice_channel.name,
                  "Delete VC", "critical")
    else:
        await ctx.respond(f"Something went wrong", ephemeral=True)


async def set_user_count_vc(ctx, voice_channel, user_count):
    rights, voice_channel = await check_permissions(ctx, voice_channel)
    if rights and voice_channel is not None:
        if user_count <= 0:
            await voice_channel.edit(user_limit=0)
            await ctx.respond(f"Removed permanent voice chanel user limit", ephemeral=True)
            await log(ctx.author.mention + " removed permanent voice channel user limit from " + voice_channel.name,
                      "Set User Count", "normal")
        if user_count > 99:
            await voice_channel.edit(user_limit=99)
            await ctx.respond(f"User limit can't be higher than 99, applied 99 as current limit",
                              ephemeral=True)
            await log(ctx.author.mention + " changed permanent voice channel user limit to 99 from "
                      + voice_channel.name, "Set User Count", "normal")
        else:
            await voice_channel.edit(user_limit=user_count)
            await ctx.respond(f"Changed permanent voice channel User Count", ephemeral=True)
            await log(ctx.author.mention + f" changed permanent voice channel user limit to {user_count} from "
                      + voice_channel.name, "Set User Count", "normal")
    else:
        await ctx.respond(f"Something went wrong", ephemeral=True)


async def check_permissions(ctx, voice_channel):
    if voice_channel is None:
        # Check for Perm User rights
        owns_permanent_vc, permanent_voice_channel = check_permanent_owner(ctx.author)
        owns_temporary_vc, temporary_voice_channel = check_temporary_owner(ctx.author)

        if owns_temporary_vc:
            return owns_temporary_vc, temporary_voice_channel
        elif owns_permanent_vc:
            return owns_permanent_vc, permanent_voice_channel
        else:
            await ctx.respond(f"You don't own an permanent Voice Channel", ephemeral=True)
            await log(ctx.author.mention + " tried to change a permanent voice channel without owning one",
                      "No Permissions", "critical")
            return False, None
    else:
        # Check for Mod rights
        mod_rights = get_mod_rights(ctx.author)
        if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
            if voice_channel.id in config.config.get("UNMODIFIABLE_CHANNEL"):
                return None, None
            else:
                return mod_rights, voice_channel
        else:
            await ctx.respond(f"You don't have Mod rights", ephemeral=True)
            await log(ctx.author.mention + " tried to change a permanent voice channel without mod rights",
                      "No Moderator Permissions", "critical")
            return False, None


def color_switch(level):
    if level == "non urgent":
        return 0x00ff00
    elif level == "default":
        return 0xffff00
    elif level == "critical":
        return 0xff0000
    else:
        return 0x00ff00


async def log(message, command, level):

    color = color_switch(level)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("[" + str(current_time) + "] " + "[" + command + "] " + str(message))
    channel = discord.utils.get(config.bot.get_all_channels(),
                                id=config.config.get("LOG_CHANNEL"),
                                type=discord.ChannelType.text)

    embed = discord.Embed(title=command, description=current_time, color=color)
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


def text_replace(match):
    return '*' * len(match.group())


def blacklist_filter(text, blacklist):
    blacklist_pattern = '|'.join(re.escape(word) for word in blacklist)
    return re.sub(blacklist_pattern, text_replace, text, flags=re.IGNORECASE)


async def vc_mod_add_permanent_role(ctx, role: discord.Role):
    mod_rights = get_mod_rights(ctx.author)

    if mod_rights:
        if role.id not in config.config.get("PERMANENT_ROLES"):
            await add_to_list(config.config["PERMANENT_ROLES"], role.id)
            await ctx.respond("Role added to list", ephemeral=True)
            await log("Admin: " + ctx.author.mention + " added " + role.mention
                            + " to the permanent VC Roles", "Add Permanent Role", "critical")
        else:
            await ctx.respond("Role already in list", ephemeral=True)
    else:
        await ctx.respond("You don't have the rights to use this command", ephemeral=True)
        await log(ctx.author.mention + " tried to use the Admin Command vc_admin_add_permanent_role", "Add Permanent Role", "critical")


async def vc_mod_remove_permanent_role(ctx, role: discord.Role):
    mod_rights = get_mod_rights(ctx.author)

    if mod_rights:
        if role.id in config.config.get("PERMANENT_ROLES"):
            await remove_from_list(config.config["PERMANENT_ROLES"], role.id)
            await ctx.respond("Role removed from list", ephemeral=True)
            await log("Admin: " + ctx.author.mention + " removed " + role.mention
                            + " from the permanent VC Roles", "Remove Permanent Role", "critical")
        else:
            await ctx.respond("Role not in list", ephemeral=True)
    else:
        await ctx.respond("You don't have the rights to use this command", ephemeral=True)
        await log(ctx.author.mention + " tried to use the Admin Command vc_admin_remove_permanent_role",
                  "Remove Permanent Role", "critical")


async def vc_mod_add_to_blacklist(ctx, word):
    mod_rights = get_mod_rights(ctx.author)

    if mod_rights:
        if word not in config.blacklist:
            config.blacklist.append(word)
            with open(config.blacklist_path, "w") as json_file:
                json.dump(config.blacklist, json_file, indent=4)
            json_file.close()
            await log(ctx.author.mention + " added the word " + word + " to the blacklist",
                      "Add to Blacklist", "critical")
            await ctx.respond("Added " + word + " to the Blacklist", ephemeral=True)
    else:
        await ctx.respond("You don't have the rights to use this command", ephemeral=True)
        await log(ctx.author.mention + " tried to use the Admin Command vc_admin_remove_permanent_role")


async def vc_mod_remove_from_blacklist(ctx, word):
    mod_rights = get_mod_rights(ctx.author)

    if mod_rights:
        if word in config.blacklist:
            config.blacklist.remove(word)
            with open(config.blacklist_path, "w") as json_file:
                json.dump(config.blacklist, json_file, indent=4)
            json_file.close()
            await log(ctx.author.mention + " removed the word " + word + " from the blacklist",
                      "Remove from Blacklist", "critical")
            await ctx.respond("Removed " + word + " from the Blacklist", ephemeral=True)
    else:
        await ctx.respond("You don't have the rights to use this command", ephemeral=True)
        await log(ctx.author.mention + " tried to use the Admin Command vc_admin_remove_from_blacklist",
                  "Remove from Blacklist", "critical")


async def vc_mod_list_blacklist(ctx):
    mod_rights = get_mod_rights(ctx.author)

    if mod_rights:
        embed = discord.Embed(title="Word Blacklist", description="List of all Blacklisted words", color=0x00ff00)
        for word in config.blacklist:
            embed.add_field(name=word, value="", inline=False)

        await ctx.respond(embed=embed, ephemeral=True)
    else:
        await ctx.respond("You don't have the rights to use this command", ephemeral=True)
        await log(ctx.author.mention + " tried to use the Admin Command vc_admin_list_blacklist",
                  "List Blacklist", "critical")
