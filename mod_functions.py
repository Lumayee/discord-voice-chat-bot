import discord
import config
import utils


# Get a list of all Roles able to create a permanent VCs
@config.bot.command(description="Mod Only! List all permanent VC roles")
async def vc_mod_list_perma_roles(ctx):
    mod_rights = utils.get_mod_rights(ctx.author)

    if mod_rights:
        embed = discord.Embed(title="Permanent VC Roles", description="List of all permanent VC roles", color=0x00ff00)
        for role in config.config.get("PERMANENT_ROLES"):
            embed.add_field(name=role, value="", inline=False)

        await ctx.respond(embed=embed, ephemeral=True)


# Unban a user from a permanent VC
@config.bot.command(description="Mod Only! unban user from VC")
async def vc_mod_unban(ctx, channel: discord.VoiceChannel, user: discord.User):
    await utils.unban_user_from_vc(ctx, channel, user)


# ban a user from a permanent VC
@config.bot.command(description="Mod Only! Ban user from VC")
async def vc_mod_ban(ctx, channel: discord.VoiceChannel, user: discord.User):
    await utils.ban_user_from_vc(ctx, channel, user)


@config.bot.user_command(name="Mod Only! Ban user from VC")
async def vc_mod_ban_app(ctx, user: discord.User):
    await utils.ban_user_from_vc(ctx, user.voice.channel, user)


# Kick a user from a permanent or temporary VC
@config.bot.command(description="Mod Only! Kick user a VC")
async def vc_mod_kick(ctx, channel: discord.VoiceChannel, user: discord.User):
    await utils.kick_user_from_vc(ctx, channel, user)


@config.bot.user_command(name="Mod Only! Kick user a VC")
async def vc_mod_kick_app(ctx, user: discord.User):
    await utils.kick_user_from_vc(ctx, user.voice.channel, user)


# Delete a permanent VC from another User
@config.bot.command(description="Mod Only! Delete VC")
async def vc_mod_delete(ctx, channel: discord.VoiceChannel):
    await utils.delete_vc(ctx, channel)


# Rename a permanent VC from another User
@config.bot.command(description="Mod Only! Rename VC")
async def vc_mod_rename(ctx, channel: discord.VoiceChannel, new_name):
    await utils.rename_vc(ctx, channel, new_name)


# Change the user limit of a permanent VC
@config.bot.command(description="Mod Only! Rename VC")
async def vc_mod_set_user_count(ctx, channel: discord.VoiceChannel, user_count: int):
    await utils.set_user_count_vc(ctx, channel, user_count)


# Remove a permanent VC Role
@config.bot.command(description="Mod Only! Add a permanent VC role")
async def vc_mod_add_permanent_role(ctx, role: discord.Role):
    await utils.vc_mod_add_permanent_role(ctx, role)


# Add a permanent VC Role
@config.bot.command(description="Mod Only! Remove a permanent VC role")
async def vc_mod_remove_permanent_role(ctx, role: discord.Role):
    await utils.vc_mod_remove_permanent_role(ctx, role)


# Add word to blacklist
@config.bot.command(description="Mod Only! Remove from blacklist")
async def vc_mod_blacklist_add(ctx, word):
    await utils.vc_mod_add_to_blacklist(ctx, word)


# Remove word from blacklist
@config.bot.command(description="Mod Only! Remove from blacklist")
async def vc_mod_blacklist_remove(ctx, word):
    await utils.vc_mod_remove_from_blacklist(ctx, word)


# List blacklist
@config.bot.command(description="Mod Only! List blacklist")
async def vc_mod_blacklist_list(ctx):
    await utils.vc_mod_list_blacklist(ctx)
