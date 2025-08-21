### UVU Email Bot Documentation

For extra information/help, please contact pierceclark07@gmail.com

Welcome to the UVU Email Bot! This bot is designed to allow easy email/message forwarding between the
Upper Valley Ultimate discord server and the UVU email list. For a detailed rundown of everything the
bot does, read on below!

# How to use this bot:

This bot does two primary things. First, it can forward emails sent to it into discord channels,
to keep the discord people in the loop with announcements. Secondly, it can "promote" discord
messages to emails: Specifically, when sending a discord message, you can choose to also send that
message as an email to the UVU Community. This last feature is slightly less helpful, but all the
functionality for it exists, so it can be used at any time. However, since there isn't a huge
demand for it at the moment, I've disabled the feature to prevent abuse. With that said, I can
enable it at any time, and theres a pretty extensive permission system put in place for added
security. For more details about that part, see below.

## Forwarding Emails to Discord:

Forwarding emails to Discord is pretty straightforward. Under the hood, the bot maintains a list
of "Routes". These routes map an email address to a Discord channel ID. When the bot receives an
email, if the sender is recognized on a route, then the message will be automatically forwarded
to the corresponding channel. Note that each email address can only map to one channel, and not
multiple! In practice this is not that much of a limitation however, since all messages sent in
a Google Group actually "send" from a single unified address (for example,
"uppervalleyultimate@googlegroups.com), even if the actual sender is a personal address. Thus,
the actual limitation here is just that each Google Group the bot is a part of can only send to
at most one channel. However, if you want, you can also add routes for personal emails to specific
channels, and you can double-up on channels if you'd like (i.e. two addresses to the same channel).
In order to "receive" these emails, the email must include "UVUbot@gmail.com" in the list of
senders: this works if the bot is included as a member of the group, or if you send it a direct
email.

### Modifying Routes:

To modify routes, three hybrid commands are made available: "addroute", "removeroute", and
"listroutes". All three of these can be used with the Discord slash command system. The first
two of these commands require at least bot-admin permissions: see below on the details for that.
Here is a description of what each command does:

    - addroute {email} {channel ID}
        This command is used to add a new route to the bot settings. Once this command is
        invoked, the new route will be tracked for all future emails. This command requires
        two additional arguments: an email address to track, and the discord channel ID of
        the desired forwarding channel. See below for details on how to get this ID. Both
        of these arguments are required.

    - removeroute {email}
        This command is used to remove a route from the bot settings, preventing future
        emails from being forwarded to the corresponding channel. This command requires as
        an argument the email to remove. Be careful, because the string is case-sensitive!
        The email you enter and the email listed from the "listroutes" command must match
        exactly for the command to work.

    - listroutes
        This command will generate a list of all currently tracked routes, and display them
        in the channel where the command was invoked. This command is the only one of these
        three that does not require any permissions to use.

### Getting Discord Channel IDs:

To add a route above, you'll need to find the Discord channel ID of the channel you want to
send to. To do this, the easiest way to get it is to enable "Developer Options" in Discord
settings. Then, you can get the channel ID by right-clicking on the channel and selecting the
"Copy Channel ID" option from the drop down. There's also a bunch of documentation on this
on the web, so I recommend googling it if you get stuck. Finally, you can also ask someone else
or (in the worst case) email me if you run into problems.

### Super-Sender Configuration

As an additional feature, there is a hard-coded list of email addresses that can be configured
to have forwarding priveledges to a hard-coded channel ID, that exists outside the scope of the
routing system. Currently this is **disabled**, but if there ever arises a need for extra ways to
send priority emails to a channel, that can be done here.

## Forwarding Discord to Email:

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

# Email Format/API Documentation:

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

# Settings and Authorization:

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

# Settings (And how to change them)

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

# Final Notes:

This was a pretty quick project for me, so there may be more functionality that would be helpful and should be
added. As always, reach out to me (pierceclark07@gmail.com) or just come find me at pickup or wherever. I'm
happy to add more functionality/improve this as needed. If its helpful, I also maintain a private github
repo with all version control data for the project if for any reason its needed (though sensitive information
like bot tokens and my google token/credentials are obviously not tracked there, so you can't run the bot from
just that information).

Let me know what your thoughts are!
Pierce
