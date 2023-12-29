import discord
import config
import utils
import json


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


@config.bot.command(description="Admin: Add word to blacklist")
async def vc_admin_add_to_blacklist(ctx, word):
    admin_rights = utils.get_admin_rights(ctx.author)

    if admin_rights:
        if word not in config.blacklist:
            config.blacklist.append(word)
            with open(config.blacklist_path, "w") as json_file:
                json.dump(config.blacklist, json_file, indent=4)
            json_file.close()
            await utils.log(ctx.author.mention + " added the word " + word + " to the blacklist")
            await ctx.respond("Added " + word + " to the Blacklist", ephemeral=True)
    else:
        await ctx.respond("You don't have the rights to use this command", ephemeral=True)
        await utils.log(ctx.author.mention + " tried to use the Admin Command vc_admin_remove_permanent_role")


@config.bot.command(description="Admin: Remove word from blacklist")
async def vc_admin_remove_from_blacklist(ctx, word):
    admin_rights = utils.get_admin_rights(ctx.author)

    if admin_rights:
        if word in config.blacklist:
            config.blacklist.remove(word)
            with open(config.blacklist_path, "w") as json_file:
                json.dump(config.blacklist, json_file, indent=4)
            json_file.close()
            await utils.log(ctx.author.mention + " removed the word " + word + " from the blacklist")
            await ctx.respond("Removed " + word + " from the Blacklist", ephemeral=True)
    else:
        await ctx.respond("You don't have the rights to use this command", ephemeral=True)
        await utils.log(ctx.author.mention + " tried to use the Admin Command vc_admin_remove_from_blacklist")


@config.bot.command(description="Admin: List Banned words")
async def vc_admin_list_blacklist(ctx):
    admin_rights = utils.get_admin_rights(ctx.author)

    if admin_rights:
        embed = discord.Embed(title="Word Blacklist", description="List of all Blacklisted words", color=0x00ff00)
        for word in config.blacklist:
            embed.add_field(name=word   , value="", inline=False)

        await ctx.respond(embed=embed, ephemeral=True)
    else:
        await ctx.respond("You don't have the rights to use this command", ephemeral=True)
        await utils.log(ctx.author.mention + " tried to use the Admin Command vc_admin_list_blacklist")

