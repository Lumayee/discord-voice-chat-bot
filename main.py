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
    # When a user joins the creation VC, create and move the user
    if after.channel and after.channel.id == config.CREATE_CHANNEL:
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

    # When a user leaves a VC, try to delete the channel
    # Check if the VC Channel is permanent
    permanent = False
    item = None

    if before.channel:
        for item in voice_channel_owners:
            if item.get("Temp_VC") == "False" and before.channel.id == item["VC_Channel_ID"]:
                permanent = True
                break

    # If the VC is permanent, update the last join time
    if item is not None and permanent:
        item["Last_Join"] = datetime.now().timestamp()
        with open(file_path, "w") as json_file:
            json.dump(voice_channel_owners, json_file, indent=4)

    # If a temporary VC is empty, delete it
    else:
        if before.channel and len(
                before.channel.members) == 0 and before.channel.id != config.CREATE_CHANNEL and not permanent:
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
        "Temp_VC": "False"
    }
    voice_channel_owners.append(entry)

    print("Permanent VC: " + str(ctx.author.name) + "(" +
          str(ctx.author.id) + ") " + "created Voice Channel " + str(entry["VC_Channel_ID"]))

    with open(file_path, "w") as json_file:
        json.dump(voice_channel_owners, json_file, indent=4)

    json_file.close()


# Slash command to change the user limit of a permanent VC
@bot.command(description="VC set User Limit")
async def vc_set_users(ctx, user_count: int):
    # Convert user_count to an integer if it's not
    user_count = int(user_count)

    # Check if the User owns a permanent VC
    owns_permanent_vc = False
    vc_id = None

    for item in voice_channel_owners:
        if ctx.author.id == item.get("User_ID") and item.get("Temp_VC") == "False":
            owns_permanent_vc = True
            vc_id = item.get("VC_Channel_ID")
            break

    if owns_permanent_vc:
        vc_channel_id = discord.utils.get(bot.get_all_channels(), id=vc_id, type=discord.ChannelType.voice)

        # Check if the channel is a VoiceChannel and then edit it
        if isinstance(vc_channel_id, discord.VoiceChannel):
            if user_count == 0:
                await vc_channel_id.edit(user_limit=0)
            else:
                await vc_channel_id.edit(user_limit=user_count)
            await ctx.respond(f"Changed permanent VC User Count", ephemeral=True)

    else:
        await ctx.respond(f"You don't own any permanent VCs", ephemeral=True)


# Slash command to change the name of a permanent VC
@bot.command(description="Rename your VC")
async def vc_rename(ctx, new_name):
    # Search the user ID in the JSON with the owners

    # Check if the User owns a permanent VC
    owns_permanent_vc = False
    vc_id = None

    for item in voice_channel_owners:
        if ctx.author.id == item.get("User_ID") and item.get("Temp_VC") == "False":
            owns_permanent_vc = True
            vc_id = item.get("VC_Channel_ID")
            break

    if owns_permanent_vc:
        # When found, get the channel class and change the name
        vc_channel_id = discord.utils.get(bot.get_all_channels(),
                                          id=int(vc_id),
                                          type=discord.ChannelType.voice)

        if isinstance(vc_channel_id, discord.VoiceChannel):
            await vc_channel_id.edit(name=new_name)
            await ctx.respond(f"Changed permanent VC Name to {new_name}", ephemeral=True)
        else:
            await ctx.respond(f"Channel with ID {vc_id} "
                              f"is not a voice channel or does not exist.", ephemeral=True)
    else:
        await ctx.respond(f"You don't own a permanent VC", ephemeral=True)


# Slash command to delete an permanent VC
@bot.command(description="Delete VC")
async def vc_delete(ctx):

    # Check if the User owns a permanent VC
    owns_permanent_vc = False
    vc_id = None

    for item in voice_channel_owners:
        if ctx.author.id == item.get("User_ID") and item.get("Temp_VC") == "False":
            owns_permanent_vc = True
            vc_id = item.get("VC_Channel_ID")
            break

    if owns_permanent_vc:
        vc_channel_id = discord.utils.get(bot.get_all_channels(),
                                          id=int(vc_id),
                                          type=discord.ChannelType.voice)

        await vc_channel_id.delete()
        await ctx.respond(f"Permanent VC deleted", ephemeral=True)

    else:
        await ctx.respond(f"You dont own an permanent VC", ephemeral=True)


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
    mod_rights = False
    for role in ctx.author.roles:
        if role.id in config.MOD_ROLES:
            mod_rights = True
            break

    if mod_rights:
        # When found, get the channel class and delete it
        vc_channel_id = discord.utils.get(bot.get_all_channels(),
                                          id=int(vc_id),
                                          type=discord.ChannelType.voice)

        if isinstance(vc_channel_id, discord.VoiceChannel):
            await vc_channel_id.delete()
            await ctx.respond(f"Deleted the voice channel", ephemeral=True)
        else:
            await ctx.respond(f"Channel with ID {vc_id} is not a voice channel or does not exist.", ephemeral=True)

    else:
        await ctx.respond(f"You don't have Moderator rights", ephemeral=True)



# Rename a permanent VC from another User
@bot.command(description="Only for Mods: Rename VC")
async def vc_mod_rename(ctx, vc_id, new_name):
    # Check if the User has a Moderator Role
    mod_rights = False
    for role in ctx.author.roles:
        if role.id in config.MOD_ROLES:
            mod_rights = True
            break

    # Try to change the name of the VC
    if mod_rights:
        vc_channel_id = discord.utils.get(bot.get_all_channels(),
                                          id=int(vc_id),
                                          type=discord.ChannelType.voice)

        if isinstance(vc_channel_id, discord.VoiceChannel):
            await vc_channel_id.edit(name=new_name)
            await ctx.respond(f"Changed permanent VC Name to {new_name}", ephemeral=True)
        else:
            await ctx.respond(f"Channel with ID {vc_id} is not a voice channel or does not exist.", ephemeral=True)

    else:
        await ctx.respond(f"You don't have Moderator rights", ephemeral=True)


bot.run(config.TOKEN)
