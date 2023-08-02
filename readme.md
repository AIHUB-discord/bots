


# bots



## Settings file:
in the `settings.json` generated by running the python app, or running the `optionshandler.py`

## Prefix setting:
The prefix that triggers the bot commands (startsWith)

## Allow setting:
you will find `allow` that is responsible for allowed servers/channels/users

how it works is really simple, its an array of regex strings to compair against (discordRole doesn't use regex, don't forget to add 2 of the `_` before discordRole):

### Structure
`serverID_channelID_authorID__discordRole__Comment_doesnt_effect_anything`

### for example if you want only server with id `123123123` to use the commands
`123123123_*_*`

### if you want only server with id `123123123` and channel id `420420420` to use the commands
`123123123_420420420_*`

### if you want only author id `420420420` to use the commands
`*_*_420420420`

### if you want only server with id `123123123` and role id `12300001` to use the commands then 
`123123123_*_*__12300001`

### if you want only role id `12300001` to use the commands then 
`__12300001`