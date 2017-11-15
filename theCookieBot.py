#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram
import re
import pickle
from unidecode import unidecode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from random import randint
from datetime import datetime, timedelta
from configparser import ConfigParser
from collections import OrderedDict
import json
import os
import sys
from threading import Thread
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from youtubeApi import YoutubeAPI


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


random4GodMsg = ['dime', 'basta', 'déjame', 'ahora no', 'ZzZzzzZzz', '¿qué te pasa?']
mimimimiStickerPath = ['/home/pi/Desktop/cookieBotData/stickers/mimimi.webp', '/home/pi/Desktop/cookieBotData/stickers/mimimi1.webp', '/home/pi/Desktop/cookieBotData/stickers/mimimi2.webp']
m3AudiosPath = []
huehuehuePath = ['/home/pi/Desktop/cookieBotData/gifs/huehuehue.mp4', '/home/pi/Desktop/cookieBotData/gifs/huehuehue1.mp4']
canTalk = True
firstMsg = True
maxValueForJob = 5
indexValueForJob = 0
messageOwner = 0
dataCookie = {}

def ini_to_dict(path):
    """ Read an ini path in to a dict
    :param path: Path to file
    :return: an OrderedDict of that path ini data
    """
    global dataCookie
    json_file = open('/home/pi/Desktop/github/TheCookieBot/data_cookie.json', 'r')
    dataCookie = json.load(json_file)
    config = ConfigParser()
    config.read(path)
    return_value=OrderedDict()
    for section in reversed(config.sections()):
        return_value[section]=OrderedDict()
        section_tuples = config.items(section)
        for itemTurple in reversed(section_tuples):
            return_value[section][itemTurple[0]] = itemTurple[1]
    return return_value

# Create the EventHandler and pass it your bot's token.
config = ConfigParser()
settings = ini_to_dict(os.path.join(os.path.dirname(__file__), "config.ini"))
updater = Updater(settings["main"]["token"])

j = updater.job_queue

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Yeheeeeeeee!', reply_to_message_id=update.message.message_id)

def help(bot, update):
    update.message.reply_text(':)')

def getRandomByValue(value):
    randomValue = randint(0, value)
    return randomValue

def randomResponse(update, bot):
    global dataCookie
    randomValue = getRandomByValue(200)
    if randomValue == 11:
        array = update.message.text.split()
        randomIndex = getRandomByValue(3)
        wasChanged = None
        if randomIndex == 0:
            wasChanged = bool(re.search(r'[VvSs]+', update.message.text))
            update.message.text = re.sub(r'[VvSs]+', 'f', update.message.text)
        elif randomIndex == 1:
            wasChanged = bool(re.search(r'[Vv]+', update.message.text))
            update.message.text = re.sub(r'[Vv]+', 'f', update.message.text)
        else:
            wasChanged = bool(re.search(r'[TtVvSsCc]+', update.message.text))
            update.message.text = re.sub(r'[TtVvSsCc]+', 'f', update.message.text)
        if wasChanged:
            update.message.reply_text(update.message.text, reply_to_message_id=update.message.message_id)
    elif randomValue == 10:
        global messageOwner
        if messageOwner == 0:
            messageOwner = '@'+update.message.from_user.username
            j.run_once(isNowJob, 10, context=update.message.chat_id)
    elif randomValue <= 9 and randomValue >= 3:
        randomMsgIndex = getRandomByValue(len(dataCookie['randomMsg']) -1)
        update.message.reply_text(dataCookie['randomMsg'][randomMsgIndex], reply_to_message_id=update.message.message_id)
    elif randomValue < 2:
        update.message.text = unidecode(update.message.text)
        update.message.text = re.sub(r'[AEOUaeou]+', 'i', update.message.text)
        update.message.reply_text(update.message.text, reply_to_message_id=update.message.message_id)
        randomMsgIndex = getRandomByValue(len(mimimimiStickerPath) -1)
        bot.send_sticker(chat_id=update.message.chat_id, sticker=open(mimimimiStickerPath[randomMsgIndex], 'rb'))


def sendGif(bot, update, pathGif):
    bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
    bot.sendDocument(chat_id=update.message.chat_id, document=open(pathGif, 'rb'))

def sendVoice(bot, update, pathVoice):
    bot.send_voice(chat_id=update.message.chat_id, voice=open(pathVoice, 'rb'))

def sendImg(bot, update, pathImg):
    bot.send_photo(chat_id=update.message.chat_id, photo=open(pathImg, 'rb'))

def isAdmin(bot, update):
    if update.message.from_user.username != None and update.message.from_user.id in get_admin_ids(bot, update.message.chat_id):
        return True
    else:
        return None

def startJobs(bot, update):
    now = datetime.now() - timedelta(days = 1)
    now = now.replace(hour=19, minute=00)
    job_daily = j.run_daily(callback_andalucia, now.time(), days=(0,1,2,3,4,5,6), context=update.message.chat_id)
    #now = now.replace(hour=2, minute=00)
    #job_daily = j.run_daily(callback_bye, now.time(), days=(0,1,2,3,4,5,6), context=update.message.chat_id)

def isNowJob(bot, job):
    global maxValueForJob
    global indexValueForJob
    global messageOwner
    global dataCookie

    indexMsg = getRandomByValue(len(dataCookie['randomJobMsg']) -1)
    bot.send_message(chat_id=job.context, text=dataCookie['randomJobMsg'][indexMsg] + " " + str(messageOwner))

    indexValueForJob+=1

    if indexValueForJob < maxValueForJob:
        j.run_once(isNowJob, 40, context=job.context)
    else:
        messageOwner = None
        indexValueForJob = 0

def gimmeTags(video, videoTags, maxTags):
    tagsIndex = 0
    if video['snippet'].get('tags') != None:
        while tagsIndex < len(video['snippet']['tags']) and tagsIndex < maxTags:
            videoTags += video['snippet']['tags'][tagsIndex] + " "
            tagsIndex+=1
    return videoTags

def saveDataSong(update):
    data = []
    try:
        json_file = open('data.txt', 'r')
        data = json.load(json_file)
    except IOError:
        data = []

    data.append(update.message.text)
    with open('data.txt', 'w') as outfile:
        json.dump(data, outfile)

    update.message.reply_text("No conseguimos encontrar la canción en Spotify :( sorry :( la añadiremos a mano...", reply_to_message_id=update.message.message_id)

def callSpotifyApi(videoTitle, videoTags, video, sp, update):
    try:
        results = sp.search(q=videoTitle, limit=1)
        if results['tracks']['total'] == 0 :
            results = sp.search(q=videoTags, limit=1)
        if results['tracks']['total'] == 0 :
            videoTags = ""
            videoTags = gimmeTags(video, videoTags, 2)
            results = sp.search(q=videoTags, limit=1)
        if results['tracks']['total'] == 0 :
            videoTags = ""
            videoTags = gimmeTags(video, videoTags, 1)
            results = sp.search(q=videoTags, limit=1)
        return results
    except:
        saveDataSong(update)

def addToSpotifyPlaylist(results, update):
    resultTracksList=results['tracks']
    idsToAdd=[]

    for j in range(len(results['tracks']['items'])):
        idsToAdd.insert(0, results['tracks']['items'][j]['id'])

    scope = 'playlist-modify playlist-modify-public user-library-read playlist-modify-private'
    token = util.prompt_for_user_token(settings["spotify"]["spotifyuser"],scope,client_id=settings["spotify"]["spotifyclientid"],client_secret=settings["spotify"]["spotifysecret"],redirect_uri='http://localhost:8000')
    sp = spotipy.Spotify(auth=token)
    results = sp.user_playlist_add_tracks(settings["spotify"]["spotifyuser"], settings["spotify"]["spotifyplaylist"], idsToAdd)
    update.message.reply_text("Añadidas " + str(len(idsToAdd)) + " canciones, gracias! :D", reply_to_message_id=update.message.message_id)

def gimmeTheSpotifyPlaylistLink(bot, update):
    update.message.reply_text('ahí te va! ' + settings["spotify"]["spotifyplaylistlink"])

def replaceYouTubeVideoName(videoTitle):
    videoTitle = re.sub(r'\([\[a-zA-Z :\'0-9\]]+\)', '', videoTitle)
    videoTitle = re.sub(r'\[[\[a-zA-Z :\'0-9\]]+\]', '', videoTitle)
    videoTitle = videoTitle.lower().replace("official video", "")
    videoTitle = videoTitle.lower().replace("official music video", "")
    videoTitle = videoTitle.lower().replace("videoclip oficiai", "")
    videoTitle = videoTitle.lower().replace("video clip oficiai", "")
    videoTitle = videoTitle.lower().replace("videoclip", "")
    return videoTitle

def echo(bot, update):
    global canTalk
    global firstMsg

    if str(update.message.chat_id) == str(settings["main"]["groupid"]):
        for i in range(len(update.message.entities)):
            if update.message.entities[i].type == 'url' and ( 'youtu.be' in update.message.text.lower() or 'youtube.com' in update.message.text.lower()):
                try:
                    videoid = ""
                    if 'youtu.be' not in update.message.text.lower():
                        videoid = update.message.text.split('v=')
                        videoid = videoid[1].split(' ')[0]
                        videoid = videoid.split('&')[0]
                    else:
                        videoid = update.message.text.split('youtu.be/')
                        videoid = videoid[1].split(' ')[0]
                        videoid = videoid.split('&')[0]
                    youtube = YoutubeAPI({'key': settings["main"]["youtubeapikey"]})
                    video = youtube.get_video_info(videoid)
                    videoTitle = video['snippet']['title'].lower()
                    videoTitle = replaceYouTubeVideoName(videoTitle)
                    videoTags = ""
                    tagsIndex = 0
                    videoTags = gimmeTags(video, videoTags, 3)
                    if videoTitle != None and videoTags != None:
                        client_credentials_manager = SpotifyClientCredentials(client_id=settings["spotify"]["spotifyclientid"], client_secret=settings["spotify"]["spotifysecret"])
                        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                        sp.trace = False
                        results = callSpotifyApi(videoTitle, videoTags, video, sp, update)

                        if results['tracks']['total'] != None and results['tracks']['total'] == 0:
                            saveDataSong(update)
                        else:
                            addToSpotifyPlaylist(results, update)
                    else:
                        saveDataSong(update)
                except:
                    saveDataSong(update)

        if update.message.text != None and "cookie para" == update.message.text.lower():
            stop(bot, update)
        elif update.message.text != None and "cookie sigue" == update.message.text.lower():
            restart(bot, update)

        if firstMsg:
            startJobs(bot, update)
            firstMsg=None

        if canTalk:
            #voice
           # if re.search(r'\<3\b', update.message.text.lower()):
           #     randomAudioIndex = getRandomByValue(len(m3AudiosPath) -1)
           #     sendVoice(bot, update, m3AudiosPath[randomAudioIndex])
            #gif
            if re.search(r'\bpfff[f]+\b', update.message.text.lower()) or '...' == update.message.text:
                randomValue = getRandomByValue(4)
                if randomValue <= 1:
                    sendGif(bot, update, '/home/pi/Desktop/cookieBotData/gifs/pffff.mp4')
            elif "gif del fantasma" in update.message.text.lower():
                sendGif(bot, update, '/home/pi/Desktop/cookieBotData/gifs/fantasma.mp4')
            elif "bukkake" in update.message.text.lower() or "galletitas" in update.message.text.lower():
                sendGif(bot, update, '/home/pi/Desktop/cookieBotData/gifs/perro.mp4')
            elif re.search(r'\bcabra\b', update.message.text.lower()):
                randomValue = getRandomByValue(4)
                if randomValue <= 1:
                    sendGif(bot, update, '/home/pi/Desktop/cookieBotData/gifs/cabra_scream.mp4')
            elif unidecode(u'qué?') == unidecode(update.message.text.lower()) or "que?" == update.message.text.lower():
                sendGif(bot, update, '/home/pi/Desktop/cookieBotData/gifs/cabra.mp4')
            elif unidecode(u'aió') == unidecode(update.message.text.lower()) or re.search(r'\baio\b', update.message.text.lower()):
                sendGif(bot, update, '/home/pi/Desktop/cookieBotData/gifs/bye.mp4')
            elif re.search(r'\breviento\b', update.message.text.lower()) or re.search(r'\brebiento\b', update.message.text.lower()):
                sendGif(bot, update, '/home/pi/Desktop/cookieBotData/gifs/acho_reviento.mp4')
            elif re.search(r'\bchoca\b', update.message.text.lower()):
                sendGif(bot, update, '/home/pi/Desktop/cookieBotData/gifs/choca.mp4')
            elif re.search(r'\bbro\b', update.message.text.lower()):
                sendGif(bot, update, '/home/pi/Desktop/cookieBotData/gifs/cat_bro.mp4')
            elif "templo" in update.message.text.lower() or "gimnasio" in update.message.text.lower():
                randomValue = getRandomByValue(4)
                if randomValue <= 1:
                    sendGif(bot, update, '/home/pi/Desktop/cookieBotData/gifs/templo.mp4')
            elif re.search(r'\bhuehue[hue]+\b', update.message.text.lower()):
                randomHuehuehueIndex = getRandomByValue(len(huehuehuePath) -1)
                sendGif(bot, update, huehuehuePath[randomHuehuehueIndex])

            #messages
            elif "cookie dame la lista" in update.message.text.lower():
                gimmeTheSpotifyPlaylistLink(bot, update)
            elif "cookie dame la config" in update.message.text.lower():
                bot.send_document(chat_id=update.message.chat_id, document=open('/home/pi/Desktop/github/TheCookieBot/data_cookie.json', 'rb'))
                bot.send_document(chat_id=update.message.chat_id, document=open('/home/pi/Desktop/github/TheCookieBot/config.ini', 'rb'))
            elif re.search(r'\bdios\b', update.message.text.lower()):
                randomValue = getRandomByValue(4)
                if randomValue < 1 :
                    indexMsg = getRandomByValue(len(random4GodMsg) -1)
                    update.message.reply_text(random4GodMsg[indexMsg], reply_to_message_id=update.message.message_id)

            # imgs

            #stickers
            elif len(update.message.text) > 4: ##mimimimimimi
                randomResponse(update, bot)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def callback_andalucia(bot, job):
    bot.send_message(chat_id=job.context, text="¡Buenoh díah, Andalucía! :D")

def callback_bye(bot, job):
    bot.send_message(chat_id=job.context, text="AIÓ")
    bot.sendChatAction(chat_id=job.context, action=telegram.ChatAction.UPLOAD_PHOTO)
    bot.sendDocument(chat_id=job.context, document=open('/home/pi/Desktop/cookieBotData/gifs/bye.mp4', 'rb'))

def stop(bot, update):
    if isAdmin(bot, update):
        global canTalk
        canTalk = None
    else:
        bot.send_message(chat_id=job.context, text="JA! No :)")

def restart(bot, update):
    if isAdmin(bot, update):
        global canTalk
        canTalk = True
    else:
        bot.send_message(chat_id=job.context, text="JA! No :)")

def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

def main():
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler('seguir', restart))
    dp.add_handler(CommandHandler('parar', stop))
    dp.add_handler(CommandHandler('damelalista', gimmeTheSpotifyPlaylistLink))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
