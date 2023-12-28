import discord
import config
import utils


# Get a list of all Roles able to create a permanent VCs
@config.bot.command(description="List all permanent VC Roles")
async def vc_mod_list_perma_roles(ctx):
    mod_rights = utils.get_mod_rights(ctx.author)

    if mod_rights:
        embed = discord.Embed(title="Permanent VC Roles", description="List of all permanent VC roles", color=0x00ff00)
        for role in config.config.get("PERMANENT_ROLES"):
            embed.add_field(name=role, value="", inline=False)

        await ctx.respond(embed=embed, ephemeral=True)


# Unban a user from a permanent VC
@config.bot.command(description="Mod: unban User from VC")
async def vc_mod_unban(ctx, channel: discord.VoiceChannel, user: discord.User):
    await utils.unban_user_from_vc(ctx, channel.id, user.id)


# ban a user from a permanent VC
@config.bot.command(description="Mod: Ban User from VC")
async def vc_mod_ban(ctx, channel: discord.VoiceChannel, user: discord.User):
    await utils.ban_user_from_vc(ctx, channel.id, user.id)


@config.bot.user_command(name="Moderator: Kick User from VC")
async def vc_mod_ban_app(ctx, user: discord.User):
    await utils.kick_user_from_vc(ctx, None, user.id)


# Kick a user from a permanent or temporary VC
@config.bot.command(description="Kick User a VC")
async def vc_mod_kick(ctx, channel: discord.VoiceChannel, user: discord.User):
    await utils.kick_user_from_vc(ctx, channel, user.id)


# Delete a permanent VC from another User
@config.bot.command(description="Only for Mods: Delete VC")
async def vc_mod_delete(ctx, channel: discord.VoiceChannel):
    await utils.delete_vc(ctx, channel.id)


# Rename a permanent VC from another User
@config.bot.command(description="Only for Mods: Rename VC")
async def vc_mod_rename(ctx, channel: discord.VoiceChannel, new_name):
    await utils.rename_vc(ctx, channel.id, new_name)


# Change the user limit of a permanent VC
@config.bot.command(description="Only for Mods: Rename VC")
async def vc_mod_set_user_count(ctx, channel: discord.VoiceChannel, user_count):
    await utils.set_user_count_vc(ctx, channel.id, user_count)
