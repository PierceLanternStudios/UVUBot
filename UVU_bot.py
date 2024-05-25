### =======================  Lantern UBC  ===============================

# This script is designed to function as a template for a generic bot,
# in a manner that is flexible enough to be expanded out for any purpose. 
# Note that this framework requires the existence of a file named "AuthData.env"
# in the local directory which contains the bot token. If this file is absent, 
# the template will not work.

# User variables:

prefix = ""         # Enter the bot prefix here (This will still be structured 
                    # towards hybrid commands, but this is required for sync)

authorized_userIDs = [466365370006241302]       # This is a list of all user IDs (integers) who are authorized
                                                # to use administrator commands on this bot (namely sync for 
                                                # right now, as it can affect the bot performance/API priviledge).
            





### ======================  Core functionality  =========================
### Packages
import discord
from discord.ext import commands, tasks


### Intents and setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=prefix, intents = intents)
discordclient = discord.Client(intents = intents)

# this is a debug ping command to detect if the bot is responding. 
@bot.command()
async def ping(ctx):
    await ctx.send("Hello, "+ ctx.author.nick)



# this is the sync command, which needs to be run for every new 
# slash command that is introduced
@bot.command(name = "sync")
async def sync(ctx):

    #check for valid user:
    if ctx.author.id not in authorized_userIDs:
        await ctx.send("Invalid user For /Sync command")
        return

    #sync commands to slash commands
    await ctx.bot.tree.sync()
    await ctx.send("Commands synced!")



### ============================  Events   ===================================
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name="Status goes here"))
    print("[LanternUBC]: [Application] online and running.")


# More events below here!




### ========= Time loop task  ================
@tasks.loop(hours = 24)
async def TimeUpdater():
    print("Performing daily update...")


    # more daily functionality below here!










### ========================  Startup  =============================
with open("AuthData.env", "r") as f:
    bot_token = f.readline()
    bot.run(bot_token)
    f.close()

    