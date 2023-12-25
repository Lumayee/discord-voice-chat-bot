import typing
import discord
import config
import json
import asyncio
from datetime import datetime

file_path = "vc_channels.json"
bot = discord.Bot()
voice_channel_owners = []


# Load the JSON file with the VCs
def load_vc():
    global voice_channel_owners

    try:
        print("Loading permanent Voice Channels:")
        with open(file_path, "r") as json_file:
            try:
                voice_channel_owners = json.load(json_file)
            except json.JSONDecodeError:
                voice_channel_owners = []
                print("Error: JSON Decode Error, creating empty JSON file")
    except FileNotFoundError:
        with open(file_path, "w") as json_file:
            json.dump([], json_file)
            print("Error: JSON File not found, creating empty JSON file")

    # Print the loaded VCs
    if voice_channel_owners:
        for item in voice_channel_owners:
            print(item)

    print("Loading completed")


def check_permanent_owner(user_id):
    # Check if the User owns a permanent VC
    owns_permanent_vc = False
    voice_channel = None

    for item in voice_channel_owners:
        if user_id == item.get("User_ID") and item.get("Temp_VC") == "False":
            owns_permanent_vc = True
            vc_id = item.get("VC_Channel_ID")

            voice_channel = discord.utils.get(bot.get_all_channels(),
                                              id=int(vc_id),
                                              type=discord.ChannelType.voice)

            break

    return owns_permanent_vc, voice_channel


def getUserFromID(user_id):
    for member in bot.get_all_members():
        if member.id == int(user_id):
            user = discord.utils.get(bot.get_all_members(), id=int(user_id))
            return user
    return None


def getVCFromID(vc_id):
    vc_channel_id = discord.utils.get(bot.get_all_channels(),
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
    for item in voice_channel_owners:
        if vc_id == item.get("VC_Channel_ID"):
            if user_id in item.get("Ban"):
                return True
    return False


def getBanList(vc_id):
    for item in voice_channel_owners:
        if vc_id == item.get("VC_Channel_ID"):
            return item.get("Ban")
    return None


def addBan(user_id, vc_id):
    for item in voice_channel_owners:
        if vc_id == item.get("VC_Channel_ID"):
            item.get("Ban").append(user_id)
            with open(file_path, "w") as json_file:
                json.dump(voice_channel_owners, json_file, indent=4)
            return True
    return False


def removeBan(user_id, vc_id):
    for item in voice_channel_owners:
        if vc_id == item.get("VC_Channel_ID"):
            item.get("Ban").remove(user_id)
            with open(file_path, "w") as json_file:
                json.dump(voice_channel_owners, json_file, indent=4)
            return True
    return False


def isBanned(user_id, vc_id):
    for item in voice_channel_owners:
        for ban in item.get("Ban"):
            if user_id == int(ban) and vc_id == item.get("VC_Channel_ID"):
                return True
    return False


def getPermaentVCIDList():
    list = []
    for item in voice_channel_owners:
        if item.get("Temp_VC") == "False":
            list.append(item.get("VC_Channel_ID"))
    return list


# After the Bot is ready
@bot.event
async def on_ready():
    load_vc()

    print(f"Logged in as {bot.user.name}")

    # Launch the check for inactive VCs
    await bot.loop.create_task(check_inactive_vcs())

    # Check for empty temporary VCs
    for item in voice_channel_owners:
        if item.get("Temp_VC") == "True":
            vc_channel_id = discord.utils.get(bot.get_all_channels(),
                                              id=int(item["VC_Channel_ID"]),
                                              type=discord.ChannelType.voice)

            if isinstance(vc_channel_id, discord.VoiceChannel) and len(vc_channel_id.members) == 0:
                await vc_channel_id.delete()
                print("Temporary VC: deleted VC with ID: " + str(item["VC_Channel_ID"]))


# When a user joins/leaves a VC
@bot.event
async def on_voice_state_update(member, before, after):
    permanentVCs = getPermaentVCIDList()

    # User Joins the create VC
    if after and after.channel and after.channel.id == int(config.CREATE_CHANNEL):
        guild = member.guild
        new_channel = await guild.create_voice_channel(f'{member.name} VC', category=after.channel.category)
        creation = await member.move_to(new_channel)

        if creation:
            print("Temporary VC: " + member.name + " created VC with ID: " + str(new_channel.id))
            # Write User ID and VC Channel ID to the json
            entry = {
                "VC_Channel_ID": after.channel.id,
                "Temp_VC": "True"
            }
            voice_channel_owners.append(entry)
            with open(file_path, "w") as json_file:
                json.dump(voice_channel_owners, json_file, indent=4)
            json_file.close()

    # User Joins a permanent VC
    elif after and after.channel and after.channel.id in permanentVCs:
        print("Permanent VC: " + member.name + " joined VC with ID: " + str(after.channel.id))
        if isBanned(member.id, after.channel.id):
            await member.move_to(None)
            return

    # User leaves a temp VC
    if before and before.channel and before.channel.id not in permanentVCs and before.channel.id != int(config.CREATE_CHANNEL):
        # If the temp VC is empty, delete it
        if len(before.channel.members) == 0:
            await before.channel.delete()
            print("Temporary VC: deleted VC with ID: " + str(before.channel.id))


# Slash Command for Bot Ping
@bot.command(description="Sends the bots latency.")
async def ping(ctx):
    await ctx.respond(f"Pong! Latency is {bot.latency} s", ephemeral=True)
    print(str(ctx.author.name) + "(" + str(ctx.author.id) + ") " +
          "requested the Bot latency, the current Latency is: " + str(bot.latency) + "s")


# Slash Command for VC Channel creation
@bot.command(description="Create VC")
async def vc_create(ctx, name: typing.Optional[str] = None):
    guild = ctx.guild
    category = discord.utils.get(guild.categories, id=int(config.VC_CATEGORY))

    # Check if the User already owns a VC
    for item in voice_channel_owners:
        if ctx.author.id == item["User_ID"]:
            await ctx.respond("You can only create one voice channel at a time.", ephemeral=True)
            print("Permanent VC: " + str(ctx.author.name) + "(" + str(ctx.author.id) + ") " +
                  "tried to create more than one permanent Voice Channels")
            return

    if not any(role.id in config.PERMANENT_ROLES for role in ctx.author.roles):
        await ctx.respond("You don't have the rights to create a permanent Voice Channel", ephemeral=True)
        print("Permanent VC: " + str(ctx.author.name) + "(" + str(ctx.author.id) + ") " +
              "tried to create a permanent Voice Channel without the right role")
        return

    # If the name was Empty, set the name to the users name
    if name is None:
        name = "Permanent VC from " + ctx.author.name

    # Create new channel, give user permissions and respond to them
    new_channel = await category.create_voice_channel(name)
    await ctx.respond(f"Voice Channel {name} was successfully created", ephemeral=True)

    # Write User ID and VC Channel ID to the json
    entry = {
        "User_ID": ctx.author.id,
        "VC_Channel_ID": new_channel.id,
        "Last_Join": datetime.now().timestamp(),
        "Temp_VC": "False",
        "Ban": []
    }
    voice_channel_owners.append(entry)

    print("Permanent VC: " + str(ctx.author.name) + "(" +
          str(ctx.author.id) + ") " + "created Voice Channel " + str(entry["VC_Channel_ID"]))

    with open(file_path, "w") as json_file:
        json.dump(voice_channel_owners, json_file, indent=4)

    json_file.close()


# Slash command to change the user limit of a permanent VC
@bot.command(description="VC set User Limit")
async def vc_set_user_count(ctx, user_count: int):
    # Convert user_count to an integer if it's not
    user_count = int(user_count)

    owns_permanent_vc, voice_channel = check_permanent_owner(ctx.author.id)

    if owns_permanent_vc:
        if isinstance(voice_channel, discord.VoiceChannel):
            # Check if the channel is a VoiceChannel and then edit it
            if isinstance(voice_channel, discord.VoiceChannel):
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

    else:
        await ctx.respond(f"You don't own any permanent VCs", ephemeral=True)


# Slash command to change the name of a permanent VC
@bot.command(description="Rename your VC")
async def vc_rename(ctx, new_name):
    # Check if the User owns a permanent VC
    owns_permanent_vc, voice_channel = check_permanent_owner(ctx.author.id)

    if owns_permanent_vc:
        if isinstance(voice_channel, discord.VoiceChannel):
            await voice_channel.edit(name=new_name)
            await ctx.respond(f"Changed permanent VC Name to {new_name}", ephemeral=True)
        else:
            await ctx.respond(f"Channel with ID {voice_channel.id} "
                              f"is not a voice channel or does not exist.", ephemeral=True)
    else:
        await ctx.respond(f"You don't own a permanent VC", ephemeral=True)


# Slash command to delete an permanent VC
@bot.command(description="Delete VC")
async def vc_delete(ctx):
    # Check if the User owns a permanent VC
    owns_permanent_vc, voice_channel = check_permanent_owner(ctx.author.id)

    if owns_permanent_vc:
        if isinstance(voice_channel, discord.VoiceChannel):
            await voice_channel.delete()
            await ctx.respond(f"Deleted the voice channel", ephemeral=True)
        else:
            await ctx.respond(f"Channel with ID {voice_channel.id} "
                              f"is not a voice channel or does not exist.", ephemeral=True)
    else:
        await ctx.respond(f"You don't own a permanent VC", ephemeral=True)


# Remove the VC Channel from the JSON, when the VC Channel is deleted
@bot.event
async def on_guild_channel_delete(channel):
    # Enter when a VC Channel is deleted
    if isinstance(channel, discord.VoiceChannel):
        deleted_channel_id = channel.id

        # Check if the VC Channel belongs to a User
        for item in voice_channel_owners:
            if deleted_channel_id == item["VC_Channel_ID"]:
                print("deleted Voice Channel " + str(item["VC_Channel_ID"]))
                voice_channel_owners.remove(item)
                # Save the updated JSON data back to the file
                with open(file_path, "w") as json_file:
                    json.dump(voice_channel_owners, json_file, indent=4)
                break  # Exit the loop once the item is found


# Delete the permanent VC, when a User is leaving the Server
@bot.event
async def on_member_remove(member):
    # Check if the VC Channel belongs to a User
    for item in voice_channel_owners:
        if member.id == item["VC_Channel_ID"]:
            if item.get("Temp_VC") == "False":
                print("Temporary VC: ")
            else:
                print("Permanent VC: ")

            deleted = voice_channel_owners.remove(item)

            if deleted:
                print(str(item["User_ID"]) + " deleted Voice Channel " + str(item["VC_Channel_ID"]))
                await item.respond(f"Permanent VC deleted", ephemeral=True)

                with open(file_path, "w") as json_file:
                    json.dump(voice_channel_owners, json_file, indent=4)
                break
            else:
                print("Error: Could not delete Voice Channel " + str(item["VC_Channel_ID"]))
                await item.respond(f"Failed to delete VC", ephemeral=True)


# Check for inactive VCs
async def check_inactive_vcs():
    while True:
        print("Checking inactive VCs")
        one_month_seconds = 30 * 24 * 60 * 60  # 30 days in seconds

        for item in voice_channel_owners:
            if (item.get("Temp_VC") == "False" and
                    (datetime.now().timestamp() - item.get("Last_Join", 0) > one_month_seconds)):
                vc_channel_id = discord.utils.get(bot.get_all_channels(),
                                                  id=int(item["VC_Channel_ID"]),
                                                  type=discord.ChannelType.voice)
                await vc_channel_id.delete()

        await asyncio.sleep(86400)  # 24 hours in seconds


# MOD Commands

# Delete a permanent VC from another User
@bot.command(description="Only for Mods: Delete VC")
async def vc_mod_delete(ctx, vc_id):
    # Check if the User has a Moderator Role
    mod_rights = getModRights(ctx.author)
    voice_channel = getVCFromID(vc_id)

    if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
        await voice_channel.delete()
        await ctx.respond(f"Deleted the voice channel", ephemeral=True)
    else:
        await ctx.respond(f"Channel with ID {vc_id} is not a voice channel or does not exist.", ephemeral=True)


# Rename a permanent VC from another User
@bot.command(description="Only for Mods: Rename VC")
async def vc_mod_rename(ctx, vc_id, new_name):
    # Check if the User has a Moderator Role
    mod_rights = getModRights(ctx.author)
    voice_channel = getVCFromID(vc_id)

    if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
        await voice_channel.edit(name=new_name)
        await ctx.respond(f"Changed permanent VC Name to {new_name}", ephemeral=True)
    else:
        await ctx.respond(f">:c", ephemeral=True)


# Kick a user from your permanent VC
@bot.command(description="Kick User from VC")
async def vc_kick(ctx, user_id):
    # Check if the User owns a permanent VC
    owns_permanent_vc, voice_channel = check_permanent_owner(ctx.author.id)

    if owns_permanent_vc:
        # Check if the channel is a VoiceChannel and then edit it
        if isinstance(voice_channel, discord.VoiceChannel):
            # Check if the user is in the VC
            for member in voice_channel.members:
                if member.id == int(user_id):
                    await member.move_to(None)
                    await ctx.respond(f"Kicked user from VC", ephemeral=True)
                    return

            await ctx.respond(f"User is not in the VC", ephemeral=True)

    else:
        await ctx.respond(f"You don't own a permanent VC", ephemeral=True)


# Kick a user from a permanent VC
@bot.command(description="Kick User a VC")
async def vc_mod_kick(ctx, vc_id, user_id):
    # Check if the User has a Moderator Role
    mod_rights = getModRights(ctx.author)
    voice_channel = getVCFromID(vc_id)

    if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
        # Check if the user is in the VC
        for member in voice_channel.members:
            if member.id == int(user_id):
                await member.move_to(None)
                await ctx.respond(f"Kicked user from VC", ephemeral=True)
                return

        await ctx.respond(f"User is not in the VC", ephemeral=True)

    else:
        await ctx.respond(f"You don't have Moderator rights", ephemeral=True)


@bot.command(description="Ban User from VC")
async def vc_ban(ctx, user_id):
    # Check if the User owns a permanent VC
    owns_permanent_vc, voice_channel = check_permanent_owner(ctx.author.id)

    if owns_permanent_vc:
        # Check if the channel is a VoiceChannel and then edit it
        if isinstance(voice_channel, discord.VoiceChannel):
            # Check if the user is in the VC
            for member in voice_channel.members:
                if member.id == int(user_id):
                    await member.move_to(None)

            if addBan(user_id, voice_channel.id):
                await ctx.respond(f"Banned user from VC", ephemeral=True)
            else:
                await ctx.respond(f"Error: Could not ban user", ephemeral=True)

    else:
        await ctx.respond(f"You don't own a permanent VC", ephemeral=True)


@bot.command(description="unban User from VC")
async def vc_unban(ctx, user_id):
    # Check if the User owns a permanent VC
    owns_permanent_vc, voice_channel = check_permanent_owner(ctx.author.id)

    if owns_permanent_vc:
        # Check if the channel is a VoiceChannel and then edit it
        if isinstance(voice_channel, discord.VoiceChannel):
            # Check if the user is in the VC
            for member in voice_channel.members:
                if member.id == int(user_id):
                    await member.move_to(None)

            if removeBan(user_id, voice_channel.id):
                await ctx.respond(f"Banned user from VC", ephemeral=True)
            else:
                await ctx.respond(f"Error: Could not ban user", ephemeral=True)

    else:
        await ctx.respond(f"You don't own a permanent VC", ephemeral=True)


@bot.command(description="Mod: Ban User from VC")
async def vc_mod_ban(ctx, vc_id, user_id):
    # Check if the User has a Moderator Role
    mod_rights = getModRights(ctx.author)
    voice_channel = getVCFromID(vc_id)

    if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
        # Check if the user is in the VC
        for member in voice_channel.members:
            if member.id == int(user_id):
                await member.move_to(None)

        if addBan(user_id, voice_channel.id):
            await ctx.respond(f"Banned user from VC", ephemeral=True)
        else:
            await ctx.respond(f"Error: Could not ban user", ephemeral=True)

    else:
        await ctx.respond(f"You don't have Moderator rights", ephemeral=True)


@bot.command(description="Mod: unban User from VC")
async def vc_mod_unban(ctx, vc_id, user_id):
    # Check if the User has a Moderator Role
    mod_rights = getModRights(ctx.author)
    voice_channel = getVCFromID(vc_id)

    if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
        if removeBan(user_id, voice_channel.id):
            await ctx.respond(f"UnBanned user from VC", ephemeral=True)
        else:
            await ctx.respond(f"Error: Could not unban user", ephemeral=True)

    else:
        await ctx.respond(f"You don't have Moderator rights", ephemeral=True)



bot.run(config.TOKEN)
