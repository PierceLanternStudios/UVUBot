### UVU Email Bot Documentation

For extra information/help, please contact pierceclark07@gmail.com

Welcome to the UVU Email Bot! This bot is designed to allow easy email forwarding between the
Upper valley ultimate discord server and the UVU Email list. Currently, the bot only works in
one direction: you can use it to copy messages from discord into an email. However, I'm thinking
about making it also copy email announcements into the discord server.

### How to use this bot:

This bot does two primary things. First, it can forward emails sent to it into discord channels,
to keep the discord people in the loop with announcements. Secondly, it can "promote" discord
messages to emails: Specifically, when sending a discord message, you can choose to also send that
message as an email to the UVU Community.

There are two ways to use this bot for sending emails: @mentioning the bot and using the built-in
slash command.

@mentioning:
If you mention the bot in a message, the message that you typed will be forwarded to the UVU
email server as an annoucement (this will also excise the @mention from the text, so it will
look in the email like a regular message). This is pretty easy and low-impact (if you were
already going to type out a long annoucement, you can just add an @mention for the bot and it
will forward it automatically). However, this notably does not leave room for a custom subject.
By default, the subject line of the emails will be "UVU: Discord announcement from [Your Name]".
Also note that the bot will not respond to @everyone, @here, or @role mentions: only a direct
@mention, in the form of @UVUBot will send an email. If you would like to set a custom subject,
you'll need to use the slash command down below.

Slash Command:
If you would like to send the email with a custom subject line, you'll need to use the slash
command. If you type "/email" into the server bar, the command interface from discord will
appear, giving you two fields to fill out in the message bar. These fields are "Subject" and
"Message". Once you fill both of these out, the bot will send an email with the custom subject
and the message. To make sure it is also seen in discord, the bot will also send a discord
message with the subject and message. Notably, this message will be sent in the channel where
you initiated the slash command, so make sure you're in the right channel.

### Email Format/API Documentation

The email format that is used contains a lot of other information besides just the subject and
message specified by the user. This can all be changed, but currently, the email also includes
a footer with:

    - My (Pierce's) contact information
    - A bot disclaimer stating that the email was sent automatically
    - A spot for a permalink to join the UVU discord server

The email is delivered by UVUbot@gmail.com, which is a gmail account I picked up for the project.
The email is sent via the gmail/google api, documentation of which can be found here:

    https://developers.google.com/gmail/api/guides

The discord bot/interaction framework is built on the discord.py API, a standard framework for
interfacing bots with discord servers. Documentation on the discord API can be found here:

    https://discord.com/developers/docs/intro

### Settings and Authorization

I wasn't sure how tight we wanted to manage the usage of this bot, so I added in extensive
authorization/settings control as well. These settings allow for rigid control over who can use the
email-sending functionality, which I think is pretty important for something like this. Here's how
it works: There are three "Tiers" of authorization that the bot recognizes. What they are, how to
obtain them, and what they can do are listed below.

Authorized_userID:
Coded into the bot are a list of discord userID's. Users with their ID on this list can perform
any action they would like with the bot, superceding all other authorization. These users are
also the only users that can perform the commands !sync , !quit , !add_ID , and !remove_ID. These
priviledges are not extended to the other roles for the following reasons:

        !sync: !sync does not need to be run except when new commands are added. Furthermore, !sync
        uses a lot of API calls, which can get my developer access priviledge to the discord API
        revoked if it is abused. For this reason, I'm reserving this command for the highest level of
        users to protect my ability to develop future projects

        !quit: !quit will shut down the bot entirely. This presents a small difficulty in that in order
        to restart the bot, it would have to be manually restarted on whatever server it is being hosted,
        which would likely involve me SSH'ing into my raspberry pi to restart it on the command line,
        which takes a while. I added this function as a sort of emergency kill switch, but I don't want
        it to be abusable by anyone because it adds a lot of extra work for me.

        !add_ID and !remove_ID: These commands will add or remove ID's to the hard coded list. Obviously
        this is only extended to those already in the list.

Administrator:
Administrator (or "Admin") is a list of roles that is tracked by the bot as being able to always use
the email send functionality, as well as being able to configure the settings of the bot (see "Settings"
below for details on using the settings). This is currently tracked by a list of role names that you
would like to deem as an "bot administrator" role. This way, you can make a role for "bot_admin"
if you would like and give them the ability to manage the bot, without having to give away server
admin as well. However, note that any user that has the discord "administrator" priviledge (not this
bot administrator, but the larger discord administrator priviledge) as part of any of their roles
will automatically be given this level of authentication for the bot. Thus, actual admins don't have
to be added to the "bot_admin" role to access the settings. See the "Settings" section below to
learn how to add or remove roles to the list of accepted roles here.

User:
User roles function similarly to the way admin roles work above. The bot keeps track of a list of role
names, and a user must have at least one of those roles in order to send a message. These users cannot
access the settings (unless they also have one of the admin roles above), and they also cannot send
messages unless they have a user role. Note that there is also an additional setting called "Require
User Roles". If this is disabled, the bot will not check user roles before sending emails, meaning
anyone in the server can send emails. This is useful for debugging, or if we don't have a comprehensive
list of user roles yet.

### Settings (And how to change them)

In order to change the settings of the bot, the "/settings" slash command can be used. This command will
only respond if the user has admin or userID priviledge, as described above. If the user is authorized,
this command will respond with a popup modal for altering the settings. All of the settings options and
their implications are described below.

    Require User Role (Boolean):
        This setting determines whether users without a role can send emails. If the setting is "True",
        only users with one of the allowed user roles will be able to send emails. If the setting is
        "False", any user can send emails using this bot. Admins and authorized userID's can send emails
        regardless of the state of this setting. To change the setting, in the field type either "True"
        or "False". Leaving the field blank will default it to the previous value (unchanged).

    Verbose Confirmations (Boolean):
        This setting determines how vocal the bot should be in confirming that emails have been sent.
        This setting exists mostly to keep channels more clean if users would like (I recommend it). If
        this setting is "True", the bot will send a full confirmation message to the channel, indicating
        that an email has been sent. If the setting is set to false, the bot will either react to the
        command message with the "mail" emoji, or send an ephemeral message that only the command user
        can see. This reduces the amount of channel messages while still providing the same degree of
        interactivity and feedback that the task has been completed.

    Admin Roles (List of strings):
        This setting is a list of all the role tags to check for when determining if a user has the "Admin"
        role for this bot. These strings are case sensitive! When entering these strings, they must be exact
        matches of the case/text used in the role name. For example, in the UVU discord server, you would
        have to type exactly "take2admin" to add that role. However, any role that already has server admin
        priviledges (such as that role) are already given full admin priviledges over the bot, so adding
        this role specifically is unecessary. NOTE: roles with spaces or commas in the name cannot be added
        to this list. For example, if the role name is "bot admin", this role can not be interpreted by the
        bot due to the middle space. In the text box, the field should be filled out as a list separated
        with commas. For example, to add the roles "take2admin" and "new_bot_admin", in the field you would
        type "take2admin,new_bot_admin". Also note that this field is absolute each time the settings are
        edited. Previous entries to the list will be deleted each time the settings are changed. Thus, leaving
        the option blank will delete all previous admin roles: they must be re-typed each time.

    User Roles (List of strings):
        This setting is a list of all the role tags to check for when determining if a user has the "User"
        role for this bot. These strings are case sensitive! When entering these strings, they must be exact
        matches of the case/text used in the role name. For example, in the UVU discord server, you would
        have to type exactly "actualhuman" to add that role. NOTE: roles with spaces or commas in the name
        cannot be added to this list. For example, if the role name is "bot admin", this role can not be
        interpreted by the  bot due to the middle space. In the text box, the field should be filled out as a
        list separated  with commas. For example, to add the roles "take2admin" and "real_human", in the
        field you would type "take2admin,real_human". Also note that this field is absolute each time the
        settings are  edited. Previous entries to the list will be deleted each time the settings are changed.
        Thus, leaving the option blank will delete all previous admin roles: they must be re-typed each time.

Once the settings have been entered and the popup dialog is confirmed, the settings will be changed to match
the entered data and a display will appear with the current listed settings. This is more of a backend note,
but these settings are also cached to a JSON file which is imported on startup. Thus, if the bot crashes or
restarts, the settings will be preserved. Additionally, if you want to change settings on startup, you can do
that directly by editing the JSON file titled "BotSettings.json".

### Final notes

This was a pretty quick project for me, so there may be more functionality that would be helpful and should be
added. As always, reach out to me (pierceclark07@gmail.com) or just come find me at pickup or wherever. I'm
happy to add more functionality/improve this as needed. If its helpful, I also maintain a private github
repo with all version control data for the project if for any reason its needed (though sensitive information
like bot tokens and my google token/credentials are obviously not tracked there, so you can't run the bot from
just that information).

Let me know what your thoughts are!
Pierce
