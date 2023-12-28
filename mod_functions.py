import discord
import config
import utils


@config.bot.command(description="List all permanent VC Roles")
async def vc_mod_listpermaroles(ctx):
    mod_rights = utils.getModRights(ctx.author)

    if mod_rights:
        embed = discord.Embed(title="Permanent VC Roles", description="List of all permanent VC roles", color=0x00ff00)
        for role in config.get("PERMANENT_ROLES"):
            embed.add_field(name=role, value="", inline=False)

        await ctx.respond(embed=embed, ephemeral=True)


@config.bot.command(description="Mod: unban User from VC")
async def vc_mod_unban(ctx, vc_id, user_id):
    await utils.unban_user_from_vc(ctx, vc_id, user_id)


@config.bot.command(description="Mod: Ban User from VC")
async def vc_mod_ban(ctx, vc_id, user_id):
    await utils.ban_user_from_vc(ctx, vc_id, user_id)


@config.bot.user_command(name="Moderator: Ban User from VC")
async def vc_mod_ban_app(ctx, user: discord.User):
    await utils.ban_user_from_vc(ctx, user.voice.id, user.id)


# Kick a user from a permanent VC
@config.bot.command(description="Kick User a VC")
async def vc_mod_kick(ctx, vc_id, user_id):
    await utils.kick_user_from_vc(ctx, vc_id, user_id)


@config.bot.user_command(name="Moderator: Kick User from VC")
async def vc_mod_ban_app(ctx, user: discord.User):
    await utils.kick_user_from_vc(ctx, None, user.id)


# Delete a permanent VC from another User
@config.bot.command(description="Only for Mods: Delete VC")
async def vc_mod_delete(ctx, vc_id):
    await utils.delete_vc(ctx, vc_id)


# Rename a permanent VC from another User
@config.bot.command(description="Only for Mods: Rename VC")
async def vc_mod_rename(ctx, vc_id, new_name):
    await utils.rename_vc(ctx, vc_id, new_name)
