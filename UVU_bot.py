### =======================  UVU Email Bot  ===============================

# This script is designed to function as a template for a generic bot,
# in a manner that is flexible enough to be expanded out for any purpose. 
# Note that this framework requires the existence of a file named "AuthData.env"
# in the local directory which contains the bot token. If this file is absent, 
# the template will not work.

# User variables:

prefix = "!"            # Enter the bot prefix here (This will still be structured 
                        # towards hybrid commands, but this is required for sync)


            



# Json storage variables
global AdminRoles, UserRoles, RequireUserRole, VerboseConfirmations, authorized_userIDs, Routes

AdminRoles = []                     # These values are set on startup via json import, if you want to change
UserRoles = []                      # these settings go edit the file "BotSettings.json" or "Routes.json" instead.
RequireUserRole = False      
VerboseConfirmations = False 
Routes = {}

authorized_userIDs = [466365370006241302]       # This is a list of all user IDs (integers) who are authorized
                                                # to use master administrator commands on this bot. This affects 
                                                # who is allowed to set regular admin roles and user roles. To 
                                                # set this, either edit the json file, or use the add/remove ID 
                                                # commands for the purpose. This list exists just as a backup.  



AnnouncementChannelID = 1246585450534273115                 # Channel ID of the whitelisted-user annoucement channel in the UVU server

ForwardEmailAddresses = ["pierceclark07@gmail.com"]         # This is a list of whitelisted email addresses which will forward to the UVU 
                                                            # discord server whenever a new email is received.

    






### ======================  Core functionality  =========================
### -------------  Packages  -----------------------
import discord
from discord.ext import commands, tasks
import datetime
import pytz
import json
from bs4 import BeautifulSoup as bs
import re

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


@bot.command(name="quit")
async def quit(ctx):
   
    #ensure user is authorized to do this
    if ctx.author.id not in authorized_userIDs:
        await ctx.send("Invalid user For /quit command")
        return
   
    #quit
    await ctx.reply("shutting down.")
    await bot.close()


@bot.command(name="add_ID")
async def Add_ID(ctx, ID:str):
    
    global authorized_userIDs
    if ctx.author.id in authorized_userIDs:
        authorized_userIDs.append(int(ID))
        ctx.reply(f"ID {ID} added to authorized ID's")
        return
    
    ctx.reply("Sorry, you aren't authorized to do that.")

@bot.command(name="remove_ID")
async def Remove_ID(ctx, ID:str):

    # protect my own ID because I developed the bot:
    if int(ID) == 466365370006241302:
        ctx.reply("Sorry, you aren't authorized to do that. Contact Pierce for more details.")
        return

    global authorized_userIDs
    if ctx.author.id in authorized_userIDs:
        authorized_userIDs.append(int(ID))
        ctx.reply(f"ID {ID} removed from authorized ID's")
        return
    
    ctx.reply("Sorry, you aren't authorized to do that.")
    return

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
        
        if str(self.VerboseConfirmationsStr).lower() in ["true", "tru", "t", "yes", "y"]:
            VerboseConfirmations = True
        elif str(self.VerboseConfirmationsStr).lower() in ["false", "fals", "f", "no", "n"]:
           VerboseConfirmations = False

        AdminRoles = str(self.AdminRolesStr).replace(" ", "").split(",")
        UserRoles = str(self.UserRolesStr).replace(" ", "").split(",")

        await interaction.response.defer()







### ============================  Route Management   ===================================
    
### Import Routes from JSON into Data:
async def importRoutes():
    try:
        with open("Routes.json", "r") as f:
            global Routes
            Routes = json.load(f)
            print("Routes Imported")
    except:
        print("Error: Failed to import Routes")


#Write out Routes data to settings file:
async def exportRoutes():
    global Routes
    with open("Routes.json", "w") as outfile:
        json.dump(Routes, outfile)
        print("[LOG]: Data written to Routes outfile.")





### ============================  Events   ===================================
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name="Status goes here"))
    print("[LanternUBC]: UVUBot online and running.")

    await importRoutes()

    #import settings
    with open("BotSettings.json", "r") as f:
        try:
            data = json.load(f)
            global AdminRoles, UserRoles, RequireUserRole, VerboseConfirmations, authorized_userIDs
            AdminRoles = data["AdminRoles"]
            UserRoles = data["UserRoles"]
            VerboseConfirmations = data['VerboseLogging']
            RequireUserRole = data["RequireUserRole"]
            authorized_userIDs = data["AuthorizedIDs"]
            print("Settings Imported")
        except:
           print("Error importing data.")
           return

        




@bot.event
async def on_message(message):

    # this is the @mention of the bot itself
    if "@1243987498007265301" in str(message.content):

        global AdminRoles, UserRoles, RequireUserRole, VerboseConfirmations
        
        #get the best thing to call the person who sent the email
        authorname = ""
        if message.author.nick != None:
            authorname = message.author.nick + f" ({message.author.name})"
        else:
            authorname = message.author.name


        #check auth and send message
        auth = CheckAuthorization(message.author, False)
        if auth:
            gmail_send_message(message.content.replace("<@1243987498007265301>", ""), authorname)

            #check to see if we should log verbosely to what just happened or discretely
            if VerboseConfirmations:
               await message.channel.send("Mirrored email sent.")
            else:
               await message.add_reaction("📨")

        



    await bot.process_commands(message)
        



### =============================   Commands   =========================================

@bot.hybrid_command(name = "email", description = "Used to forward a message to the email server!")
async def email(ctx, subject: str, message:str):


    #get the best thing to call the person who sent the email
    authorname = ""
    if ctx.author.nick != None:
       authorname = ctx.author.nick + f" ({ctx.author.name})"
    else:
       authorname = ctx.author.name

    #check auth and send email
    if CheckAuthorization(ctx.author, False):

        #send the email
        email = gmail_send_message(message, authorname, "UVU: " +subject)

        #inform people that things have happened
        await ctx.reply(f"\n**Subject: {subject}**\n{message}")
    
    # if they dont have auth:
    else:
       await ctx.reply("Sorry, you don't have permission to use this bot.", ephemeral = True)
    
    return  



    



@bot.hybrid_command(name = "settings", description = "Configure bot settings. Only available to admins.")
async def ConfigureSettings(ctx):
   
    #first check permissions
    auth = CheckAuthorization(ctx.author, True)

    if not auth:
        ctx.reply("Sorry, you don't have administrator.")
        return
    

    #get user settings input from the modal and reply with the details
    settings_modal = SettingsModal()
    await ctx.interaction.response.send_modal(settings_modal)
    await settings_modal.wait()


    global AdminRoles, UserRoles, RequireUserRole, VerboseConfirmations

    #format lists nicely:
    AdminRolesText = ""
    UserRolesText = ""
    for i in AdminRoles: AdminRolesText += f"{i}, "
    for i in UserRoles : UserRolesText += f"{i}, "

    #generate embed
    embed = discord.Embed(title= ("Bot Settings"),  color= 62975,  timestamp = datetime.datetime.now(pytz.timezone("US/Eastern")))
    embed.add_field(name="Admin Roles", value= AdminRolesText[:-2],inline=False)    
    embed.add_field(name="User Roles", value= UserRolesText[:-2],inline=False)    
    embed.add_field(name="Require User Role", value= str(RequireUserRole),inline=False)    
    embed.add_field(name="Verbose Logging", value = str(VerboseConfirmations),inline=False)  

    await ctx.send(f"Bot settings updated:", embed= embed)
    
    #push all this to a json
    data = {
            "AdminRoles" : AdminRoles,
            "UserRoles" : UserRoles,
            "VerboseLogging" : VerboseConfirmations,
            "RequireUserRole" : RequireUserRole,
            "AuthorizedIDs" : authorized_userIDs, 
        }
    
    #write out
    with open("BotSettings.json", "w") as outfile:
        json.dump(data, outfile)
        print("[LOG]: Data written to outfile.")


    return
   





# A small helper (NON HYBRID) command to force an email check.
# This process is on a task loop anyway (and will be completed
# automatically every minute), but in case you want to quickly 
# force one without waiting for that, this tool is available.
@bot.command(name = "ce")
async def CheckForNewEmails(ctx):
    print("Checking for new emails...")
    await ctx.reply("Checking for new emails now!")

    await CheckForNewEmails()




# A command used to remove routes
@bot.hybrid_command(name = "addroute", description="Add an email-to-discord forwarding route.")
async def addroute(ctx, email:str, channel_id:str):

    if not CheckAuthorization(ctx.author, False):
        await ctx.reply("Error: You are not authorized to perform this action. Contact an admin/dev for help.")
        return

    # ensure they formatted the Channel ID correctly
    if not channel_id.isdigit():
        await ctx.reply("Error: Make sure your 'Channel' field is the target channel ID number! Please contact an admin/dev for details.")
        return

    # if all checks pass, Add the route to the Route object and write out
    global Routes
    Routes[email] = channel_id
    await ctx.reply(f"New email route added: `{email}` → <#{channel_id}>")
    await exportRoutes()




# A command used to remove routes
@bot.hybrid_command(name = "removeroute", description="Add an email-to-discord forwarding route.")
async def removeroute(ctx, email:str):

    if not CheckAuthorization(ctx.author, False):
        await ctx.reply("Error: You are not authorized to perform this action. Contact an admin/dev for help.")
        return

    # double check that we actually have a route with that email:
    global Routes
    if email not in Routes.keys():
        await ctx.reply("Error: No route found with that email address.")
        return

    # if all checks pass, remove the route to the Route object and write out
    await ctx.reply(f"Email route removed: `{email}` → <#{Routes.pop(email)}>")
    await exportRoutes()



# List Route data in embed:
@bot.hybrid_command(name="listroutes", description="List all the current email routing data.", alias=["lr", "listroute", "list"])
async def listroutes(ctx):
    global Routes

    #generate an embed:
    embed = discord.Embed(title="Email Routing Status:", color=discord.Colour.red(), timestamp= datetime.datetime.now())
    for i in Routes.keys():
        embed.add_field(name=f"{i} → <#{Routes[i]}>", value="")

    await ctx.reply("Here are the currently tracked Routes:", embed=embed)





### =========================   Permissions  ============================


#check if a given user is authorized to perform an action:
def CheckAuthorization(author, RequiresAdmin:bool):

    global AdminRoles, UserRoles, RequireUserRole, VerboseConfirmations, authorized_userIDs
   
    #first check if they are in the master op list:
    if author.id in authorized_userIDs:
        return True
   
    #second check to see if they are in the list of approved roles:
    for i in author.roles:
        if i.name in AdminRoles or i.permissions.administrator or (i.name in UserRoles and not RequiresAdmin) or (not RequireUserRole and not RequiresAdmin):
            return True
    
    #if neither check passed, return false
    return False

    




###  ======================  Sending Emails  ====================================
def gmail_send_message(emailcontent, user, subject = None):
  """Create and send an email message
  Print the returned  message id
  Returns: Message object, including message id

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """

  #check if we were passed a subject in
  if subject != None:
      mail_subject = subject
  else:
     mail_subject = f"UVU: discord message from {user}"


    # AUTHENTICATION
  SCOPES = ["https://mail.google.com"]
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
    #mail subject is handled above
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






### ======================  Receiving Emails + Task Loop  =========================

# Task loop to check for new emails
@tasks.loop(minutes=1)
async def CheckForNewEmails():

    # AUTHENTICATION
    SCOPES = ["https://mail.google.com"]
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



        #make the client and stuff

    service = build("gmail", "v1", credentials=creds)
    unreadmsgs = service.users().messages().list(userId = "me", labelIds = ["INBOX", "UNREAD"]).execute()

    #return cases where we have no new messages
    if unreadmsgs["resultSizeEstimate"] == 0 or unreadmsgs == None:
        return
    
    #and now if we do have unread messages:
    msg_list = unreadmsgs["messages"]

    print("\n")
    for msg in msg_list:
        msg_id = msg["id"]
        fullmessage = service.users().messages().get(userId = "me", id = msg_id).execute()
        payload = fullmessage["payload"]
        headers = payload["headers"]

        for i in headers:
            if i["name"] == "Subject":
                msgSubject = i["value"]
                #print(f"Subject: {i['value']}")

            if i["name"] == "From":
                msgFrom = i['value']
                #print(f"From: {i['value']}")

            
        mssg_parts = payload['parts'] # fetching the message parts
        part_one  = mssg_parts[0] # fetching first element of the part 
        part_body = part_one['body'] # fetching body of the message
        part_data = part_body['data'] # fetching data from the body
        clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
        clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
        clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
        soup = bs(clean_two , "lxml" )
        mssg_body = str(soup.body())[4:-5]
        body_string = clean_two.decode('utf-8')

        

        #mark the message as read
        #service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()


        #print(f"Message Body: {mssg_body}")


        #check to see if email address is stored in a Route, and if so send discord ping:
        global Routes
        for i in Routes.keys():
            if i in msgFrom:
                await FormatEmailForDiscord(msgSubject, body_string, int(Routes[i]))
                return


        # Otherwise check for a super-sender:
        for i in ForwardEmailAddresses:
            if i in msgFrom:
                await FormatEmailForDiscord(msgSubject, body_string)






async def FormatEmailForDiscord(Subject:str, Message:str, channelID: int = None):

    # format message to display reply-lines correctly:
    pattern = re.compile(r'(?m)^[ \t]*>[ \t]*(?:\r)?$', flags=re.MULTILINE)
    Message = pattern.sub('> ', Message) 
    Message = re.sub(r'> $', "", Message)


    # chunk long messages to split into embeds
    chunks = [Message[i:i+1000] for i in range(0, len(Message), 1000)]

    # iterate over each chunk by 12 characters to try and find a better split point
    for idx, chunk in enumerate(chunks): 
        if idx == len(chunks) - 1:      # on the last chunk, can't move any characters forward
            break


        for charIdx in range(1,20):       # step over 20 characters:
            if chunk[-charIdx] == " " or chunk[-charIdx] == '\n':
                chunks[idx + 1] = chunk[-charIdx:] + chunks[idx + 1]
                chunks[idx] = chunk[:-charIdx]
                break


    # generate first embed:
    color = discord.Colour.random()
    embed = discord.Embed(title=Subject, color= color)
    embed.add_field(name="", value=chunks[0])


    embeds=[embed]
    for idx, chunk in enumerate(chunks[1:]):
        if idx == len(chunks) - 2:
            newEmbed = discord.Embed(color= color, timestamp= datetime.datetime.now())
            newEmbed.set_footer(text = "This message generated automatically from the UVU email server.")  
        else:
            newEmbed = discord.Embed(color= color)
        newEmbed.add_field(name="", value=chunk)
        embeds.append(newEmbed)


    if channelID == None:
        await bot.get_channel(AnnouncementChannelID).send(embeds= embeds)

    else:
        await bot.get_channel(channelID).send(embeds= embeds)




        




### ========================  Startup  =============================
with open("AuthData.env", "r") as f:
    bot_token = f.readline()
    bot.run(bot_token)
    f.close()











        


    
    