import json
import discord
import config
import utils


# When a user joins/leaves a VC
@config.bot.event
async def on_voice_state_update(member, before, after):
    permanent_vcs = utils.get_permanent_vc_list()

    # User Joins the creation VC
    if after and after.channel and after.channel.id == int(config.config.get("CREATE_CHANNEL")):
        guild = member.guild
        new_channel = await guild.create_voice_channel(f'{member.name} VC', category=after.channel.category)
        await member.move_to(new_channel)

        if isinstance(new_channel, discord.VoiceChannel):
            print("Temporary VC: " + member.name + " created VC with ID: " + str(new_channel.id))
            # Write User ID and VC Channel ID to the json
            entry = {
                "VC_Channel_ID": after.channel.id,
                "Temp_VC": "True",
                "User_ID": member.id
            }

            utils.append_to_json(entry)
            await utils.log("Temporary VC: " + member.mention + " created VC with ID: " + str(new_channel.id))

        else:
            await member.send("Failed to create VC")
            await new_channel.delete()

    # User leaves a temp VC
    if before and before.channel and before.channel.id not in permanent_vcs and before.channel.id != int(
            config.config.get("CREATE_CHANNEL")):
        # If the temp VC is empty, delete it
        if len(before.channel.members) == 0:
            await before.channel.delete()
            print("Temporary VC: deleted VC with ID: " + str(before.channel.id))
            await utils.log("Temporary VC: deleted VC with ID: " + str(before.channel.id))


# Slash Command for Bot Ping
@config.bot.command(description="Sends the bots latency.")
async def ping(ctx):
    await ctx.respond(f"Pong! Latency is {config.bot.latency} s", ephemeral=True)
    print(str(ctx.author.name) + "(" + str(ctx.author.id) + ") " +
          "requested the Bot latency, the current Latency is: " + str(config.bot.latency) + "s")


# Remove the VC Channel from the JSON, when the VC Channel is deleted
@config.bot.event
async def on_guild_channel_delete(channel):
    # Enter when a VC Channel is deleted
    if isinstance(channel, discord.VoiceChannel):
        deleted_channel_id = channel.id

        # Check if the VC Channel belongs to a User
        for item in config.voice_channel_owners:
            if deleted_channel_id == item["VC_Channel_ID"]:
                print("deleted Voice Channel " + str(item["VC_Channel_ID"]))
                config.voice_channel_owners.remove(item)
                # Save the updated JSON data back to the file
                with open(config.file_path, "w") as json_file:
                    json.dump(config.voice_channel_owners, json_file, indent=4)
                break  # Exit the loop once the item is found


# Delete the permanent VC, when a User is leaving the Server
@config.bot.event
async def on_member_remove(member):
    # Check if the VC Channel belongs to a User
    for item in config.voice_channel_owners:
        if member.id == item["VC_Channel_ID"]:
            if item.get("Temp_VC") == "False":
                print("Temporary VC: ")
            else:
                print("Permanent VC: ")

            deleted = config.voice_channel_owners.remove(item)

            if deleted:
                print(str(item["User_ID"]) + " deleted Voice Channel " + str(item["VC_Channel_ID"]))
                await item.respond(f"Permanent VC deleted", ephemeral=True)

                with open(config.file_path, "w") as json_file:
                    json.dump(config.voice_channel_owners, json_file, indent=4)
                break
            else:
                print("Error: Could not delete Voice Channel " + str(item["VC_Channel_ID"]))
                await item.respond(f"Failed to delete VC", ephemeral=True)


# Get the help message
@config.bot.command(description="Help")
async def vc_help(ctx):
    embed = discord.Embed(title="Help", description="Commands for the VC Bot", color=0x915F40)

    # General Settings
    embed.add_field(name="**General Settings**", value="\u200B", inline=False)
    embed.add_field(name="/ping", value="Displays the bot's latency.", inline=False)
    embed.add_field(name="/vc_create", value="Creates a temporary voice channel (VC).", inline=False)
    embed.add_field(name="/vc_set_user_count", value="Sets the user limit for your permanent VC.", inline=False)
    embed.add_field(name="/vc_rename", value="Renames your permanent VC.", inline=False)
    embed.add_field(name="/vc_delete", value="Deletes your permanent VC.", inline=False)
    embed.add_field(name="/vc_kick", value="Kicks a user from your permanent VC.", inline=False)
    embed.add_field(name="/vc_ban", value="Bans a user from your permanent VC.", inline=False)
    embed.add_field(name="/vc_unban", value="Unbans a user from your permanent VC.", inline=False)
    embed.add_field(name="/vc_help", value="Shows this help message.", inline=False)

    # Mod Settings
    embed.add_field(name="**Mod Settings**", value="\u200B", inline=False)
    embed.add_field(name="/vc_mod_delete", value="Deletes a permanent VC.", inline=False)
    embed.add_field(name="/vc_mod_rename", value="Renames a permanent VC.", inline=False)
    embed.add_field(name="/vc_mod_kick", value="Kicks a user from a permanent VC.", inline=False)
    embed.add_field(name="/vc_mod_ban", value="Bans a user from a permanent VC.", inline=False)
    embed.add_field(name="/vc_mod_unban", value="Unbans a user from a permanent VC.", inline=False)
    embed.add_field(name="/vc_mod_list_perma_roles", value="Lists all permanent VC roles.", inline=False)
    embed.add_field(name="/vc_mod_add_permanent_role", value="Adds a permanent role.", inline=False)
    embed.add_field(name="/vc_mod_remove_permanent_role", value="Removes a permanent role.", inline=False)
    embed.add_field(name="/vc_mod_add_to_blacklist", value="Adds a user to the blacklist.", inline=False)
    embed.add_field(name="/vc_mod_remove_from_blacklist", value="Removes a user from the blacklist.", inline=False)
    embed.add_field(name="/vc_mod_list_blacklist", value="Lists all users on the blacklist.", inline=False)

    await ctx.respond(embed=embed, ephemeral=True)

