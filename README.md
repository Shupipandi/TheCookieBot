# TheCookieBot

## Requirements

Runs with python 3 =)

Install dependencies (Linux):
```
pip3 install python-telegram-bot —upgrade
```
```
pip3 install unidecode
```
```
pip3 install spotipy
```
```
pip3 install python-dateutil --user
```
## Start

Use "python3" or your configurated command for version 3

```
python3 ./theCookieBot.py
```

### Windows
Install dependencies:
```
pip install python-telegram-bot
```
```
pip install unidecode
```
```
pip install spotipy
```
```
pip install python-dateutil --user
```
## Start

Use "python3" or your configurated command for version 3

```
python ./theCookieBot.py
```

## For test

We need to change the token value in config.ini file: token=<token_id value> with a token given by botFather (ask for more info ;) ;) )

After that, we need to change the groupid value in config.ini too because cookieBot is filtered for just one group (for private use :) ) 

### How to get the groupId
```
Add the bot in a group with read permission and just send a message.
After that you need to go to:

https://api.telegram.org/bot< bot token_id value >/getUpdates

And save the chat_id value in config.ini with groupid name.
```

## Youtube and Spotify Api
Register the app in next links and save the api keys, client_id and client_secret values in config.ini:

https://developer.spotify.com/my-applications

https://console.developers.google.com/apis/credentials

If you want to censor a word or a song, just add it in youtubeCensor.json array object.


## Required files for correct functionaly
youtubeCensor.json -> ```["string", "string"]```

dateConfig.json -> 
```
{
  "name": "mañana",
  "value": "1",
  "type": "day"
}, {
  "name": "pasado",
  "value": "2",
  "type": "day"
}]
```

userNames.json -> 
```
[{
	"name": "keyword",
	"value": "telegramId"
}]
```
data_cookie.json.

## How works Cookie
### Commands
#### Add Youtube songs or Spotify songs to Spotify List
```
cookie mete Numb Linkin Park -- 
cookie mete <songname> <groupName - Not necessary if is the first song in Spotify with the songname> 

```
``` 
<some text>  https://www.youtube.com/watch?v=hJ_eVIZkjZE --
<some text>  <youtube link video wt complete url or shorted url>
Cookie get the video name and remove all text that be inside () and [] to search in Spotify API.
If he can't find the song he will try with the different video-tags of youtube

or a spotify song link with "track/<idsong>-/whatever https://open.spotify.com/track/1TrUEdT8FmBmcKVyfucbnw?si=BXGgTDv_Qs-8-Sv_NdrBHA

```
#### Remember that...
```
cookie recuerda a las hh:mm some text -> remember to the user that sent it some text at that hour of same day or next day is the time was passed.
cookie recuerda el dd/mm/yyyy some text -> remember to the user that sent it some text at actual hour/min.
cookie recuerda el dd/mm/yyyy a las hh:mm some text -> remember to the user that sent it some text at actual hour/min.
cookie recuerda a <@username/realName/name keyword in userNames.json> a las hh:mm some text -> remember to that user some text in selected date.
cookie recuerda a <@username/realName/name keyword in userNames.json> el dd/mm/yyyy some text -> remember to that user some text in selected date.
cookie recuerda a <@username/realName/name keyword in userNames.json> el dd/mm/yyyy a las hh:mm some text -> remember to that user some text in selected date.
cookie recuerda <dateConfigName == mañana/pasado/pasadomañana/luego/después> some text -> remember to that user some text in selected date.
cookie recuerda a <username> <dateConfigName == mañana/pasado/pasadomañana/luego/después> some text -> remember to that user some text in selected date.
cookie recuerda a <username> el <weekday> a las hh:mm some text -> remember to that user some text in selected date.
```
#### Add new data...
```
cookie añade random <some text> -> add new data to "randomMsg" array
cookie añade repite <some text> -> add new data to "randomJobMsg" array
```

## Special Thanks

Spotipy is from -> https://github.com/plamere/spotipy 

Ypirqui from @kokuma -> https://github.com/juanalonso/ypirqui

## Extraball
### Send messages like a ninja

https://api.telegram.org/bot< bot token_id value >/sendMessage?chat_id=< chat_id value >&text=< text_value >
