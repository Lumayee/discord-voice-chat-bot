import discord
import typing
import config
import utils
from datetime import datetime


# Slash Command for VC Channel creation
@config.bot.command(description="Create VC")
async def vc_create(ctx, vc_name: typing.Optional[str] = None):
    guild = ctx.guild
    category = discord.utils.get(guild.categories, id=int(config.config.get("VC_CATEGORY")))

    # Check if the User already owns a VC
    for item in config.voice_channel_owners:
        if ctx.author.id == item["User_ID"]:
            await ctx.respond("You can only create one voice channel at a time.", ephemeral=True)
            print("Permanent VC: " + str(ctx.author.name) + "(" + str(ctx.author.id) + ") " +
                  "tried to create more than one permanent Voice Channels")
            return

    # Check if the User has the right role
    if not any(role.id in config.config.get("PERMANENT_ROLES") for role in ctx.author.roles):
        await ctx.respond("You don't have the rights to create a permanent Voice Channel", ephemeral=True)
        print("Permanent VC: " + str(ctx.author.name) + "(" + str(ctx.author.id) + ") " +
              "tried to create a permanent Voice Channel without the right role")
        return

    # If the name was Empty, set the name to the users name
    if vc_name is None:
        vc_name = "Permanent VC from " + ctx.author.name

    # Create new channel, give user permissions and respond to them
    new_channel = await category.create_voice_channel(vc_name)
    await ctx.respond(f"Voice Channel {vc_name} was successfully created", ephemeral=True)

    # Write User ID and VC Channel ID to the json
    entry = {
        "User_ID": ctx.author.id,
        "VC_Channel_ID": new_channel.id,
        "Last_Join": datetime.now().timestamp(),
        "Temp_VC": "False",
        "Ban": []
    }

    utils.append_to_json(entry)

    print("Permanent VC: " + str(ctx.author.name) + "(" +
          str(ctx.author.id) + ") " + "created Voice Channel " + str(entry["VC_Channel_ID"]))


# Remove the ban from a user
@config.bot.command(description="unban User from VC")
async def vc_unban(ctx, user_id):
    await utils.unban_user_from_vc(ctx, None, user_id)


@config.bot.user_command(name="Unban User from your VC")
async def vc_unban_app(ctx, user: discord.User):
    await utils.unban_user_from_vc(ctx, None, user.id)


# Ban a user from your permanent VC
@config.bot.command(description="Ban User from VC")
async def vc_ban(ctx, user_id):
    await utils.ban_user_from_vc(ctx, None, user_id)


@config.bot.user_command(name="Ban User from your VC")
async def vc_ban_app(ctx, user: discord.User):
    await utils.ban_user_from_vc(ctx, None, user.id)


# Kick a user from your permanent VC
@config.bot.command(description="Kick User from VC")
async def vc_kick(ctx, user_id):
    await utils.kick_user_from_vc(ctx, None, user_id)


@config.bot.user_command(name="Kick User from your VC")
async def vc_app_kick(ctx, user: discord.User):
    await utils.kick_user_from_vc(ctx, None, user.id)


# Slash command to change the name of a permanent VC
@config.bot.command(description="Rename your VC")
async def vc_rename(ctx, new_name):
    await utils.rename_vc(ctx, None, new_name)


# Slash command to delete an permanent VC
@config.bot.command(description="Delete VC")
async def vc_delete(ctx):
    await utils.delete_vc(ctx, None)


# Slash command to change the user limit of a permanent VC
@config.bot.command(description="VC set User Limit")
async def vc_set_user_count(ctx, user_count: int):
    await utils.set_user_count_vc(ctx, None, user_count)
