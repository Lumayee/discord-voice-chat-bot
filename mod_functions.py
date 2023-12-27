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
    # Check if the User has a Moderator Role
    mod_rights = utils.getModRights(ctx.author)
    voice_channel = utils.getVCFromID(vc_id)

    if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
        if utils.removeBan(user_id, voice_channel.id):
            await ctx.respond(f"UnBanned user from VC", ephemeral=True)
        else:
            await ctx.respond(f"Error: Could not unban user", ephemeral=True)

    else:
        await ctx.respond(f"You don't have Moderator rights", ephemeral=True)


#@config.bot.user_command(name="Mod: Ban User from VC App")
@config.bot.command(description="Mod: Ban User from VC")
async def vc_mod_ban(ctx, vc_id, user_id):
    # Check if the User has a Moderator Role
    mod_rights = utils.getModRights(ctx.author)
    voice_channel = utils.getVCFromID(vc_id)

    if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
        # Check if the user is in the VC
        for member in voice_channel.members:
            if member.id == int(user_id):
                await member.move_to(None)

        if utils.addBan(user_id, voice_channel.id):
            await ctx.respond(f"Banned user from VC", ephemeral=True)
        else:
            await ctx.respond(f"Error: Could not ban user", ephemeral=True)

    else:
        await ctx.respond(f"You don't have Moderator rights", ephemeral=True)


@config.bot.user_command(name="Moderator: Ban User from VC")
async def vc_mod_ban_app(ctx, user: discord.User):
    # Check if the User has a Moderator Role
    mod_rights = utils.getModRights(ctx.author)
    voice_channel = utils.getVCFromID(user.voice.channel.id)

    if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
        # Check if the user is in the VC
        for member in voice_channel.members:
            if member.id == int(user.id):
                await member.move_to(None)

        if utils.addBan(user.id, voice_channel.id):
            await ctx.respond(f"Banned user from VC", ephemeral=True)
        else:
            await ctx.respond(f"Error: Could not ban user", ephemeral=True)

    else:
        await ctx.respond(f"You don't have Moderator rights", ephemeral=True)



# Kick a user from a permanent VC
@config.bot.command(description="Kick User a VC")
async def vc_mod_kick(ctx, vc_id, user_id):
    # Check if the User has a Moderator Role
    mod_rights = utils.getModRights(ctx.author)
    voice_channel = utils.getVCFromID(vc_id)

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


@config.bot.user_command(name="Moderator: Kick User from VC")
async def vc_mod_ban_app(ctx, user: discord.User):
    # Check if the User has a Moderator Role
    mod_rights = utils.getModRights(ctx.author)
    voice_channel = utils.getVCFromID(not user.voice.channel.id)

    if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
        # Check if the user is in the VC
        for member in voice_channel.members:
            if member.id == int(user.id):
                await member.move_to(None)
                await ctx.respond(f"Kicked user from VC", ephemeral=True)
                return

        await ctx.respond(f"User is not in the VC", ephemeral=True)

    else:
        await ctx.respond(f"You don't have Moderator rights", ephemeral=True)


# Delete a permanent VC from another User
@config.bot.command(description="Only for Mods: Delete VC")
async def vc_mod_delete(ctx, vc_id):
    # Check if the User has a Moderator Role
    mod_rights = utils.getModRights(ctx.author)
    voice_channel = utils.getVCFromID(vc_id)

    if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
        await voice_channel.delete()
        await ctx.respond(f"Deleted the voice channel", ephemeral=True)
    else:
        await ctx.respond(f"Channel with ID {vc_id} is not a voice channel or does not exist.", ephemeral=True)


# Rename a permanent VC from another User
@config.bot.command(description="Only for Mods: Rename VC")
async def vc_mod_rename(ctx, vc_id, new_name):
    # Check if the User has a Moderator Role
    mod_rights = utils.getModRights(ctx.author)
    voice_channel = utils.getVCFromID(vc_id)

    if mod_rights and isinstance(voice_channel, discord.VoiceChannel):
        await voice_channel.edit(name=new_name)
        await ctx.respond(f"Changed permanent VC Name to {new_name}", ephemeral=True)
    else:
        await ctx.respond(f">:c", ephemeral=True)
