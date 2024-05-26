### =======================  UVU Email Bot  ===============================

# This script is designed to function as a template for a generic bot,
# in a manner that is flexible enough to be expanded out for any purpose. 
# Note that this framework requires the existence of a file named "AuthData.env"
# in the local directory which contains the bot token. If this file is absent, 
# the template will not work.

# User variables:

prefix = "!"            # Enter the bot prefix here (This will still be structured 
                        # towards hybrid commands, but this is required for sync)

authorized_userIDs = [466365370006241302]       # This is a list of all user IDs (integers) who are authorized
                                                # to use master administrator commands on this bot. This affects 
                                                # who is allowed to set regular admin roles and user roles. 
            



# Json storage variables

global AdminRoles, UserRoles, RequireUserRole, VerboseConfirmations

AdminRoles = []
UserRoles = []
RequireUserRole = False      
VerboseConfirmations = False         


    






### ======================  Core functionality  =========================
### -------------  Packages  -----------------------
import discord
from discord.ext import commands, tasks
import datetime
import pytz
import json

# google packages
import os
import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


### ----------  Environment Variables  ----------------
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'





### -----------  Intents and setup  --------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=prefix, intents = intents)
discordclient = discord.Client(intents = intents)

# this is a debug ping command to detect if the bot is responding. 
@bot.command()
async def ping(ctx):
    await ctx.send("Hello, "+ str(ctx.author.nick))



# this is the sync command, which needs to be run for every new 
# slash command that is introduced
@bot.command(name = "sync")
async def sync(ctx):

    #check for valid user:
    if ctx.author.id not in authorized_userIDs:
        await ctx.send("Invalid user For /Sync command")
        return

    #sync commands to slash commands
    print("beginning sync...")
    await ctx.bot.tree.sync()
    await ctx.send("Commands synced!")
    print("sync completed")


@bot.command
async def quit(ctx):
   
    #ensure user is authorized to do this
    if ctx.author.id not in authorized_userIDs:
        await ctx.send("Invalid user For /quit command")
        return
   
    #quit
    await ctx.reply("shutting down.")
    quit()


### ========================= End Core Functionality  =================================


### =========================  Modal Classes  ===============================
class SettingsModal(discord.ui.Modal, title='Configure Settings'):
    RequireUserRoleStr = discord.ui.TextInput(label='Require a User Role? (True or False)', style=discord.TextStyle.short,max_length=5,required=False)
    VerboseConfirmationsStr = discord.ui.TextInput(label='Verbose Response Logging? (True or False)', style=discord.TextStyle.short,max_length=5,required=False)
    AdminRolesStr = discord.ui.TextInput(label= "Extra bot admin roles (list w/ commas):",style=discord.TextStyle.long,required=False)
    UserRolesStr = discord.ui.TextInput(label= "Roles which can use the bot (list w/ commas):",style=discord.TextStyle.long,required=False)

    
    async def on_submit(self, interaction: discord.Interaction):
                
        global AdminRoles, UserRoles, RequireUserRole, VerboseConfirmations

        if str(self.RequireUserRoleStr).lower() in ["true", "tru", "t", "yes", "y"]:
            RequireUserRole = True
        elif str(self.RequireUserRoleStr).lower() in ["false", "fals", "f", "no", "n"]:
           RequireUserRole = False
        
        print(str(self.VerboseConfirmationsStr))
        if str(self.VerboseConfirmationsStr).lower() in ["true", "tru", "t", "yes", "y"]:
            VerboseConfirmations = True
        elif str(self.VerboseConfirmationsStr).lower() in ["false", "fals", "f", "no", "n"]:
           VerboseConfirmations = False

        AdminRoles = str(self.AdminRolesStr).replace(" ", "").split(",")
        UserRoles = str(self.UserRolesStr).replace(" ", "").split(",")

        await interaction.response.defer()




### ============================  Events   ===================================
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name="Status goes here"))
    print("[LanternUBC]: UVUBot online and running.")

    #import settings
    with open("BotSettings.json", "r") as f:
        try:
            data = json.load(f)
            global AdminRoles, UserRoles, RequireUserRole, VerboseConfirmations
            AdminRoles = data["AdminRoles"]
            UserRoles = data["UserRoles"]
            VerboseConfirmations = data['VerboseLogging']
            RequireUserRole = data["RequireUserRole"]
        except:
           print("Error importing data.")
           return

        
        print("Settings Imported")




@bot.event
async def on_message(message):

    if "@1243987498007265301" in str(message.content):

        await message.channel.send("you rang?")
        
        #get the best thing to call the person who sent the email
        authorname = ""
        if message.author.nick != None:
            authorname = message.author.nick + f" ({message.author.name})"
        else:
            authorname = message.author.name
        gmail_send_message(message.content.replace("<@1243987498007265301>", ""), authorname)
        



    await bot.process_commands(message)
        



### =============================   Commands   =========================================

@bot.hybrid_command(name = "email", description = "Used to forward a message to the email server!")
async def email(ctx, message:str):

    #inform people that things have happened
    await ctx.reply("emailed!")
    print(message)

    #get the best thing to call the person who sent the email
    authorname = ""
    if ctx.author.nick != None:
       authorname = ctx.author.nick + f" ({ctx.author.name})"
    else:
       authorname = ctx.author.name

    email = gmail_send_message(message, authorname)

    



@bot.hybrid_command(name = "settings", description = "Configure bot settings. Only available to admins.")
async def ConfigureSettings(ctx):
   
    #first check permissions
    auth = CheckAuthorization(ctx.author, True)

    if not auth:
        ctx.reply("Sorry, you don't have administrator.")
        return
    

    #get user settings input from the modal and reply with the details
    await ctx.interaction.response.send_modal(SettingsModal())

    global AdminRoles, UserRoles, RequireUserRole, VerboseConfirmations
    print(AdminRoles)
    embed = discord.Embed(title= ("Bot Settings"),  color= 62975,  timestamp = datetime.datetime.now(pytz.timezone("US/Eastern")))
    embed.add_field(name="Admin Roles", value= AdminRoles,inline=False)    
    embed.add_field(name="User Roles", value= UserRoles,inline=False)    
    embed.add_field(name="Require User Role", value= str(RequireUserRole),inline=False)    
    embed.add_field(name="Verbose Logging", value = str(VerboseConfirmations),inline=False)  

    await ctx.send(f"Bot settings updated:", embed= embed)
    
    #push all this to a json
    data = {
            "AdminRoles" : AdminRoles,
            "UserRoles" : UserRoles,
            "VerboseLogging" : VerboseConfirmations,
            "RequireUserRole" : RequireUserRole,
        }
    
    #write out
    with open("BotSettings.json", "w") as outfile:
        json.dump(data, outfile)
        print("[LOG]: Data written to outfile.")

        print(AdminRoles)

    return
   









### ========= Time loop task  ================
@tasks.loop(hours = 24)
async def TimeUpdater():
    print("Performing daily update...")


    # more daily functionality below here!

### =========================   Permissions and JSON Recovery  ============================


#check if a given user is authorized to perform an action:
def CheckAuthorization(author, RequiresAdmin:bool):
   
    #first check if they are in the master op list:
    if author.id in authorized_userIDs:
        return True
   
    #second check to see if they are in the list of approved roles:
    for i in author.roles:
        if i.name in AdminRoles or i.permissions.administrator or (i.name in UserRoles and not RequiresAdmin):
            return True
    
    #if neither check passed, return false
    return False

    




###  ======================  Sending Emails  ====================================
def gmail_send_message(emailcontent, user):
  """Create and send an email message
  Print the returned  message id
  Returns: Message object, including message id

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """


    # AUTHENTICATION
  SCOPES = ["https://www.googleapis.com/auth/userinfo.email","https://www.googleapis.com/auth/gmail.modify"]
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())



    #make the email
  try:
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    message.set_content(f"Heres a UVU Discord announcement from {user}:\n\n'{emailcontent}'\n\n<i>Beep boop, I'm a bot. For help/information, please contact pierceclark07@gmail.com .</i>")
    

    #=== old way of making messages in case I ever need it
    """message["To"] = "pierceclark07@gmail.com"
    message["From"] = "UVUbot@gmail.com"
    message["Subject"] = f"Discord message from {user}"
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}"""



    # === new way thats better because HTML
    discord_joinlink = "{link}"
    mail_subject = f"UVU: discord message from {user}"
    mail_body = f'<p>UVU Discord announcement from {user}:</p>\
<h3 style="padding-left: 40px;">{emailcontent}</h3>\
<p style="padding-left: 40px;">~{user}</p>\
<hr />\
<p><em>You can join the UVU Discord server here! {discord_joinlink}</em></p>\
<p><em><small>beep boop, I\'m a bot. This action was performed automatically by a user in the UVU discord server. For help or information about the bot, please contact <a href="mailto:pierceclark07@gmail.com">pierceclark07@gmail.com</a> or phantomfoolery / another admin in the UVU discord.<br /></small></em></p>'




    message2 = {
            'raw': base64.urlsafe_b64encode(
                f'MIME-Version: 1.0\n'
                f'Content-Type: text/html; charset="UTF-8"\n'
                f"From: UVUbot@gmail.com\n"
                f"To: {'pierceclark07@gmail.com'}\n"
                f"Subject: {mail_subject}\n\n"
                f"{mail_body}"
                .encode("utf-8")
            ).decode("utf-8")
        }
    # ===



    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=message2)
        .execute()
    )
    print(f'Message Id: {send_message["id"]}')
  except HttpError as error:
    print(f"An error occurred: {error}")
    send_message = None
  return send_message






### ========================  Startup  =============================
with open("AuthData.env", "r") as f:
    bot_token = f.readline()
    bot.run(bot_token)
    f.close()











        


    
    