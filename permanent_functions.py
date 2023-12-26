import discord
import json
import typing
import file_handling
import config
import utils
from datetime import datetime


# Slash Command for VC Channel creation
@config.bot.command(description="Create VC")
async def vc_create(ctx, name: typing.Optional[str] = None):
    guild = ctx.guild
    category = discord.utils.get(guild.categories, id=int(config.config.get("VC_CATEGORY")))

    # Check if the User already owns a VC
    for item in config.voice_channel_owners:
        if ctx.author.id == item["User_ID"]:
            await ctx.respond("You can only create one voice channel at a time.", ephemeral=True)
            print("Permanent VC: " + str(ctx.author.name) + "(" + str(ctx.author.id) + ") " +
                  "tried to create more than one permanent Voice Channels")
            return

    if not any(role.id in config.config.get("PERMANENT_ROLES") for role in ctx.author.roles):
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
    config.voice_channel_owners.append(entry)

    print("Permanent VC: " + str(ctx.author.name) + "(" +
          str(ctx.author.id) + ") " + "created Voice Channel " + str(entry["VC_Channel_ID"]))

    with open(config.file_path, "w") as json_file:
        json.dump(config.voice_channel_owners, json_file, indent=4)

    json_file.close()


@config.bot.command(description="unban User from VC")
async def vc_unban(ctx, user_id):
    # Check if the User owns a permanent VC
    owns_permanent_vc, voice_channel = utils.check_permanent_owner(ctx.author.id)

    if owns_permanent_vc:
        # Check if the channel is a VoiceChannel and then edit it
        if isinstance(voice_channel, discord.VoiceChannel):
            # Check if the user is in the VC
            for member in voice_channel.members:
                if member.id == int(user_id):
                    await member.move_to(None)

            if utils.removeBan(user_id, voice_channel.id):
                await ctx.respond(f"Banned user from VC", ephemeral=True)
            else:
                await ctx.respond(f"Error: Could not ban user", ephemeral=True)

    else:
        await ctx.respond(f"You don't own a permanent VC", ephemeral=True)


@config.bot.command(description="Ban User from VC")
async def vc_ban(ctx, user_id):
    # Check if the User owns a permanent VC
    owns_permanent_vc, voice_channel = utils.check_permanent_owner(ctx.author.id)

    if owns_permanent_vc:
        # Check if the channel is a VoiceChannel and then edit it
        if isinstance(voice_channel, discord.VoiceChannel):
            # Check if the user is in the VC
            for member in voice_channel.members:
                if member.id == int(user_id):
                    await member.move_to(None)

            if utils.addBan(user_id, voice_channel.id):
                await ctx.respond(f"Banned user from VC", ephemeral=True)
            else:
                await ctx.respond(f"Error: Could not ban user", ephemeral=True)

    else:
        await ctx.respond(f"You don't own a permanent VC", ephemeral=True)


# Kick a user from your permanent VC
@config.bot.command(description="Kick User from VC")
async def vc_kick(ctx, user_id):
    # Check if the User owns a permanent VC
    owns_permanent_vc, voice_channel = utils.check_permanent_owner(ctx.author.id)

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


# Slash command to change the name of a permanent VC
@config.bot.command(description="Rename your VC")
async def vc_rename(ctx, new_name):
    # Check if the User owns a permanent VC
    owns_permanent_vc, voice_channel = utils.check_permanent_owner(ctx.author.id)

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
@config.bot.command(description="Delete VC")
async def vc_delete(ctx):
    # Check if the User owns a permanent VC
    owns_permanent_vc, voice_channel = utils.check_permanent_owner(ctx.author.id)

    if owns_permanent_vc:
        if isinstance(voice_channel, discord.VoiceChannel):
            await voice_channel.delete()
            await ctx.respond(f"Deleted the voice channel", ephemeral=True)
        else:
            await ctx.respond(f"Channel with ID {voice_channel.id} "
                              f"is not a voice channel or does not exist.", ephemeral=True)
    else:
        await ctx.respond(f"You don't own a permanent VC", ephemeral=True)


# Slash command to change the user limit of a permanent VC
@config.bot.command(description="VC set User Limit")
async def vc_set_user_count(ctx, user_count: int):
    # Convert user_count to an integer if it's not
    user_count = int(user_count)

    owns_permanent_vc, voice_channel = utils.check_permanent_owner(ctx.author.id)

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
