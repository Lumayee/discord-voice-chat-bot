import discord
import file_handling
import config
import utils
import permanent_functions
import mod_functions
import base_functions

# After the Bot is ready
@config.bot.event
async def on_ready():
    file_handling.load_vc()

    print(f"Logged in as {config.bot.user.name}")

    # Launch the check for inactive VCs
    await config.bot.loop.create_task(utils.check_inactive_vcs())

    # Check for empty temporary VCs
    for item in config.voice_channel_owners:
        if item.get("Temp_VC") == "True":
            vc_channel_id = discord.utils.get(config.bot.get_all_channels(),
                                              id=int(item["VC_Channel_ID"]),
                                              type=discord.ChannelType.voice)

            if isinstance(vc_channel_id, discord.VoiceChannel) and len(vc_channel_id.members) == 0:
                await vc_channel_id.delete()
                print("Temporary VC: deleted VC with ID: " + str(item["VC_Channel_ID"]))


file_handling.load_config()
file_handling.load_blacklist()

if config.config["TOKEN"]:
    config.bot.run(config.config["TOKEN"])
else:
    print("No Token found in config.json")
