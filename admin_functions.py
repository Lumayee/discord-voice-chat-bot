import discord
import config
import utils


@config.bot.command(description="Admin: Add a permanent VC Role")
async def vc_admin_add_permanent_role(ctx, role: discord.Role):
    admin_rights = utils.get_admin_rights(ctx.author)

    if admin_rights:
        if role.id not in config.config.get("PERMANENT_ROLES"):
            await utils.add_to_list(config.config["PERMANENT_ROLES"], role.id)
            await ctx.respond("Role added to list", ephemeral=True)
            await utils.log("Admin: " + ctx.author.mention + " added " + role.mention
                            + " to the permanent VC Roles")
        else:
            await ctx.respond("Role already in list", ephemeral=True)
    else:
        await ctx.respond("You don't have the rights to use this command", ephemeral=True)
        await utils.log(ctx.author.mention + " tried to use the Admin Command vc_admin_add_permanent_role")


@config.bot.command(description="Admin: Remove a permanent VC Role")
async def vc_admin_remove_permanent_role(ctx, role: discord.Role):
    admin_rights = utils.get_admin_rights(ctx.author)

    if admin_rights:
        if role.id in config.config.get("PERMANENT_ROLES"):
            await utils.remove_from_list(config.config["PERMANENT_ROLES"], role.id)
            await ctx.respond("Role removed from list", ephemeral=True)
            await utils.log("Admin: " + ctx.author.mention + " removed " + role.mention
                            + " from the permanent VC Roles")
        else:
            await ctx.respond("Role not in list", ephemeral=True)
    else:
        await ctx.respond("You don't have the rights to use this command", ephemeral=True)
        await utils.log(ctx.author.mention + " tried to use the Admin Command vc_admin_remove_permanent_role")





