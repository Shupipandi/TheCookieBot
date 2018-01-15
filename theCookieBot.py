#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram
import re
import pickle
from unidecode import unidecode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from random import randint
from datetime import datetime, timedelta
import dateutil.parser
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
from operator import itemgetter

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

dataPath = os.path.join(os.path.dirname(__file__)) + '/data'

random4GodMsg = ['dime', 'basta', 'déjame',
                 'ahora no', 'ZzZzzzZzz', '¿qué te pasa?']
mimimimiStickerPath = ['/stickers/mimimi.webp',
                       '/stickers/mimimi1.webp', '/stickers/mimimi2.webp']
m3AudiosPath = []
huehuehuePath = ['/gifs/huehuehue.mp4', '/gifs/huehuehue1.mp4']
canTalk = True
firstMsg = True
maxValueForJob = 5
indexValueForJob = 0
messageOwner = 0
dataCookie = {}
weekdayConstant = ['lunes', 'martes', 'miércoles',
                   'jueves', 'viernes', 'sábado', 'domingo']


def ini_to_dict(path):
    """ Read an ini path in to a dict
    :param path: Path to file
    :return: an OrderedDict of that path ini data
    """
    global dataCookie
    json_file = open(
        os.path.join(os.path.dirname(__file__)) + '/data_cookie.json', 'r')
    dataCookie = json.load(json_file)
    config = ConfigParser()
    config.read(path)
    return_value = OrderedDict()
    for section in reversed(config.sections()):
        return_value[section] = OrderedDict()
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
    update.message.reply_text(
        'Yeheeeeeeee!', reply_to_message_id=update.message.message_id)


def help(bot, update):
    update.message.reply_text(':)')


def checkHourToRemember(msg, timeObject):
    # Check if hour
    msgArray = msg.split(" ")
    msgHourData = msgArray[0]
    if (msgArray[0] == "a" and "la" in msgArray[1]):
        msgHourData = msgArray[2]
        msg = msg.replace(msgArray[0] + " " + msgArray[1] + " ", "", 1)
    if ":" in msgHourData:
        hourDataSplitted = msgHourData.split(":")
        timeObject["hour"] = hourDataSplitted[0]
        timeObject["min"] = hourDataSplitted[1]
        msg = msg.replace(msgHourData + " ", "", 1)
        if int(timeObject["min"]) > 59:
            hours = int(timeObject["hour"]) + 1
            mins = int(timeObject["min"]) - 59
            timeObject["hour"] = hours
            timeObject["min"] = mins
    elif isinstance(msgHourData, int):
        timeObject["hour"] = msgHourData
        msg = msg.replace(msgHourData + " ", "", 1)

    return msg, timeObject


def checkRememberDate(now, timeObject, isWeekday):
    if isWeekday == None:
        if "type" in timeObject and timeObject["type"] == "day":
            now = now + timedelta(days=int(timeObject["value"]))
        elif "type" in timeObject and timeObject["type"] == "hour":
            now = now + timedelta(hours=int(timeObject["value"]))

    if "hour" in timeObject and timeObject["hour"] != None:
        now = now.replace(hour=int(timeObject["hour"]))
        if timeObject["min"] != None:
            now = now.replace(minute=int(timeObject["min"]))
    return now


def replaceStr(msg, str):
    if str in msg:
        msg = msg.replace(str + " ", "", 1)
    return msg


def checkDayDifference(diffDayCount, now, timeObject):
    if diffDayCount == 0 and "hor" in timeObject and now.hour <= int(timeObject["hour"]):
        if "min" in timeObject and now.minute < int(timeObject["min"]):
            print("nice hour")
        else:
            diffDayCount += 1
    return diffDayCount


def getUsernameToNotify(msg, update):
    data = []
    try:
        json_file = open('userNames.json', 'r')
        data = json.load(json_file)
    except IOError:
        data = []

    msgArray = msg.split(" ")
    index = 0
    while index < len(data):
        if data[index]["name"] in msgArray[1]:
            msg = msg.replace(msgArray[0] + " " + msgArray[1] + " ", "", 1)
            return data[index]["value"], msg
        index += 1
    return update.message.from_user.name, msg


def rememberJobs(bot, update, msg):
    timeObject = checkTimeToRemember(msg)
    usernameToNotify, msg = getUsernameToNotify(msg, update)
    # with key words in config json
    if timeObject != None:
        msg = msg.replace(timeObject["name"] + " ", "", 1)
        msg, timeObject = checkHourToRemember(msg, timeObject)

        msgArray = msg.split(" ")
        msg = replaceStr(msg, "que")

        now = datetime.now()
        now = checkRememberDate(now, timeObject, None)
        if datetime.now() > now:
            now = now + timedelta(days=1)

    # with dd/mm/yyyy config
    elif re.search(r'([0-9]+/[0-9]+/[0-9]+)', msg):
        msgArray = msg.split(" ")
        msg = replaceStr(msg, "el")

        dateWithoutSplit = re.search(r'([0-9]+/[0-9]+/[0-9]+)', msg)
        dateString = dateWithoutSplit.group(0)
        dateSplitted = dateString.split('/')
        now = datetime.now()

        msg = replaceStr(msg, dateString)
        msg = replaceStr(msg, "que")

        now = now.replace(int(dateSplitted[2]), int(
            dateSplitted[1]), int(dateSplitted[0]))
        timeObject = {}
        msg, timeObject = checkHourToRemember(msg, timeObject)
        now = checkRememberDate(now, timeObject, None)
        if datetime.now() > now:
            now = now + timedelta(days=1)

    # with weekday config
    else:
        msgArray = msg.split(" ")
        msg = replaceStr(msg, "el")

        found = None
        index = 0
        while index < len(weekdayConstant) and found != True:
            if weekdayConstant[index] in msg:
                found = True
                msg = msg.replace(weekdayConstant[index] + " ", "", 1)
            else:
                index += 1
        now = datetime.now()
        todayNumber = now.weekday()
        diffDayCount = 0
        # check how many days is from today
        if found:
            if int(todayNumber) < index:
                diffDayCount = index - int(todayNumber) + 1
            else:
                diffDayCount = (6 - int(todayNumber)) + index + 1

        msg = replaceStr(msg, "que")

        timeObject = {}
        msg, timeObject = checkHourToRemember(msg, timeObject)
        now = checkRememberDate(now, timeObject, True)
        diffDayCount = checkDayDifference(
            diffDayCount, datetime.now(), timeObject)
        now = now + timedelta(days=diffDayCount)

    update.message.reply_text(
        "Vale", reply_to_message_id=update.message.message_id)
    now = now.replace(second=0)
    saveMessageToRemember(
        usernameToNotify, msg, now.isoformat())
    j.run_once(callback_remember, now, context=update.message.chat_id)


def saveMessageToRemember(username, msg, when):
    data = []
    try:
        json_file = open('memories.json', 'r')
        data = json.load(json_file)
        data.append({'username': username, 'msg': msg, 'when': when})
    except IOError:
        data = [{'username': username, 'msg': msg, 'when': when}]

    with open('memories.json', 'w') as outfile:
        json.dump(data, outfile)


def loadMemories():
    try:
        json_file = open('memories.json', 'r')
        data = json.load(json_file)
    except IOError:
        data = {}
    data = json.dumps(
        {'data': data})
    data = json.loads(data)
    return data["data"]


def gimmeMyMemories():
    data = loadMemories()
    data = sorted(
        data,
        key=lambda x: datetime.strptime(x['when'], '%Y-%m-%dT%H:%M:%S.%f'), reverse=True
    )
    # msg = data[0]
    msg = data.pop()
    with open('memories.json', 'w') as outfile:
        json.dump(data, outfile)
    return msg


def callback_remember(bot, job):
    msg = gimmeMyMemories()
    bot.send_message(chat_id=job.context, text="EH! " +
                     msg["username"] + " te recuerdo que " + msg["msg"])


def checkTimeToRemember(msg):
    data = []
    try:
        json_file = open('dateConfig.json', 'r')
        data = json.load(json_file)
    except IOError:
        return None
    index = 0
    while index < len(data):
        if data[index]["name"] in msg:
            return data[index]
        index += 1
    return None


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
            update.message.text = re.sub(
                r'[TtVvSsCc]+', 'f', update.message.text)
        if wasChanged:
            update.message.reply_text(
                update.message.text, reply_to_message_id=update.message.message_id)
            bot.send_sticker(chat_id=update.message.chat_id, sticker=open(
                os.path.join(os.path.dirname(__file__)) +
                '/data' + '/stickers/faurio.webp', 'rb'))
    elif randomValue == 10:
        global messageOwner
        if messageOwner == 0:
            messageOwner = '@' + update.message.from_user.username
            j.run_once(isNowJob, 10, context=update.message.chat_id)
    elif randomValue <= 9 and randomValue >= 3:
        randomMsgIndex = getRandomByValue(len(dataCookie['randomMsg']) - 1)
        update.message.reply_text(
            dataCookie['randomMsg'][randomMsgIndex], reply_to_message_id=update.message.message_id)
    elif randomValue < 2:
        update.message.text = unidecode(update.message.text)
        update.message.text = re.sub(r'[AEOUaeou]+', 'i', update.message.text)
        update.message.reply_text(
            update.message.text, reply_to_message_id=update.message.message_id)
        randomMsgIndex = getRandomByValue(len(mimimimiStickerPath) - 1)
        bot.send_sticker(chat_id=update.message.chat_id, sticker=open(
            dataPath + mimimimiStickerPath[randomMsgIndex], 'rb'))


def sendGif(bot, update, pathGif):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=telegram.ChatAction.UPLOAD_PHOTO)
    bot.sendDocument(chat_id=update.message.chat_id,
                     document=open(pathGif, 'rb'))


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
    now = datetime.now() - timedelta(days=1)
    now = now.replace(hour=19, minute=00)
    job_daily = j.run_daily(callback_andalucia, now.time(), days=(
        0, 1, 2, 3, 4, 5, 6), context=update.message.chat_id)
    data = loadMemories()
    for item in data:
        j.run_once(callback_remember, dateutil.parser.parse(
            item["when"]), context=update.message.chat_id)
    #now = now.replace(hour=2, minute=00)
    #job_daily = j.run_daily(callback_bye, now.time(), days=(0,1,2,3,4,5,6), context=update.message.chat_id)


def isNowJob(bot, job):
    global maxValueForJob
    global indexValueForJob
    global messageOwner
    global dataCookie

    indexMsg = getRandomByValue(len(dataCookie['randomJobMsg']) - 1)
    bot.send_message(chat_id=job.context,
                     text=dataCookie['randomJobMsg'][indexMsg] + " " + str(messageOwner))

    indexValueForJob += 1

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
            tagsIndex += 1
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

    update.message.reply_text(
        "No conseguimos encontrar la canción en Spotify :( sorry :( la añadiremos a mano...", reply_to_message_id=update.message.message_id)


def callSpotifyApi(videoTitle, videoTags, video, sp, update):
    try:
        results = sp.search(q=videoTitle, limit=1)
        if results['tracks']['total'] == 0:
            results = sp.search(q=videoTags, limit=1)
        if results['tracks']['total'] == 0:
            videoTags = ""
            videoTags = gimmeTags(video, videoTags, 2)
            results = sp.search(q=videoTags, limit=1)
        if results['tracks']['total'] == 0:
            videoTags = ""
            videoTags = gimmeTags(video, videoTags, 1)
            results = sp.search(q=videoTags, limit=1)
        return results
    except:
        saveDataSong(update)


def addToSpotifyPlaylist(results, update):
    resultTracksList = results['tracks']
    idsToAdd = []

    for j in range(len(results['tracks']['items'])):
        idsToAdd.insert(0, results['tracks']['items'][j]['id'])

    scope = 'playlist-modify playlist-modify-public user-library-read playlist-modify-private'
    token = util.prompt_for_user_token(settings["spotify"]["spotifyuser"], scope, client_id=settings["spotify"]
                                       ["spotifyclientid"], client_secret=settings["spotify"]["spotifysecret"], redirect_uri='http://localhost:8000')
    sp = spotipy.Spotify(auth=token)
    results = sp.user_playlist_add_tracks(
        settings["spotify"]["spotifyuser"], settings["spotify"]["spotifyplaylist"], idsToAdd)


def gimmeTheSpotifyPlaylistLink(bot, update):
    update.message.reply_text(
        'ahí te va! ' + settings["spotify"]["spotifyplaylistlink"])


def replaceYouTubeVideoName(videoTitle):
    videoTitle = re.sub(r'\([\[a-zA-Z :\'0-9\]]+\)', '', videoTitle)
    videoTitle = re.sub(r'\[[\[a-zA-Z :\'0-9\]]+\]', '', videoTitle)
    videoTitle = videoTitle.lower().replace("official video", "")
    videoTitle = videoTitle.lower().replace("official music video", "")
    videoTitle = videoTitle.lower().replace("videoclip", "")
    videoTitle = videoTitle.lower().replace("video clip", "")
    videoTitle = videoTitle.lower().replace("oficial", "")
    return videoTitle


def censorYoutubeVideo(videoTitle):
    json_file = open(os.path.join(os.path.dirname(
        __file__), "youtubeCensor.json"), 'r')
    youtubeCensorData = json.load(json_file)

    for item in youtubeCensorData:
        if item in videoTitle:
            return True
    return None


def connectToSpotifyAndCheckAPI(update, videoTitle, videoTags, video):
    client_credentials_manager = SpotifyClientCredentials(
        client_id=settings["spotify"]["spotifyclientid"], client_secret=settings["spotify"]["spotifysecret"])
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    sp.trace = False
    results = callSpotifyApi(videoTitle, videoTags, video, sp, update)

    if results == None or (results['tracks']['total'] != None and results['tracks']['total'] == 0):
        saveDataSong(update, None)
    else:
        addToSpotifyPlaylist(results, update)


def addDataToJson(text):
    msg = replaceStr(text, "cookie añade")
    msgSplitted = msg.split(" ")
    msg = replaceStr(msg, msgSplitted[0])
    if msgSplitted[0] == "random":
        dataCookie['randomMsg'].append  (msg)
    elif msgSplitted[0] == "repite":
        dataCookie['randomJobMsg'].append(msg)

    with open('data_cookie.json', 'w') as outfile:
        json.dump(dataCookie, outfile)


def echo(bot, update):
    global canTalk
    global firstMsg

    if str(update.message.chat_id) == str(settings["main"]["groupid"]):
        if update.message.text != None and "cookie para" == update.message.text.lower():
            stop(bot, update)
        elif update.message.text != None and "cookie sigue" == update.message.text.lower():
            restart(bot, update)

        if firstMsg:
            startJobs(bot, update)
            firstMsg = None

        if "cookie recuerda" in update.message.text.lower() or "cookie recuerdame" in update.message.text.lower() or "cookie recuérdame" in update.message.text.lower():
            msg = update.message.text.lower()
            msgSplit = msg.split(" ")
            msg = msg.replace(
                msgSplit[0] + " " + msgSplit[1] + " ", "")
            for i in range(len(update.message.entities)):
                if update.message.entities[i].type == 'url':
                    url = update.message.text[int(update.message.entities[i]["offset"]):int(int(update.message.entities[i]["offset"])+int(update.message.entities[i]["length"]))]
                    msg= msg.replace(url.lower(), url)
            rememberJobs(bot, update, msg)

        for i in range(len(update.message.entities)):
            if update.message.entities[i].type == 'url' and ('youtu.be' in update.message.text.lower() or 'youtube.com' in update.message.text.lower()):
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
                    youtube = YoutubeAPI(
                        {'key': settings["main"]["youtubeapikey"]})
                    video = youtube.get_video_info(videoid)
                    videoTitle = video['snippet']['title'].lower()
                    videoTitle = replaceYouTubeVideoName(videoTitle)

                    if censorYoutubeVideo(videoTitle):
                        update.message.reply_text(
                            '...', reply_to_message_id=update.message.message_id)
                    else:
                        videoTags = ""
                        tagsIndex = 0
                        videoTags = gimmeTags(video, videoTags, 3)
                        if videoTitle != None and videoTags != None:
                            connectToSpotifyAndCheckAPI(
                                update, videoTitle, videoTags, video)
                        else:
                            saveDataSong(update, None)
                except:
                    saveDataSong(update, None)

        if canTalk:

            if "cookie añade" in update.message.text.lower():
                videoTitle = update.message.text.lower().replace("cookie añade ", "")

                if censorYoutubeVideo(videoTitle):
                    update.message.reply_text(
                        'No. :)', reply_to_message_id=update.message.message_id)
                else:
                    connectToSpotifyAndCheckAPI(
                        update, videoTitle, [], None)

            # voice
           # if re.search(r'\<3\b', update.message.text.lower()):
           #     randomAudioIndex = getRandomByValue(len(m3AudiosPath) -1)
           #     sendVoice(bot, update, m3AudiosPath[randomAudioIndex])
            # gif
            elif re.search(r'\bpfff[f]+\b', update.message.text.lower()) or '...' == update.message.text:
                randomValue = getRandomByValue(4)
                if randomValue <= 1:
                    sendGif(bot, update, dataPath + '/gifs/pffff.mp4')
            elif "gif del fantasma" in update.message.text.lower():
                sendGif(bot, update, dataPath + '/gifs/fantasma.mp4')
            elif "bukkake" in update.message.text.lower() or "galletitas" in update.message.text.lower():
                sendGif(bot, update, dataPath + '/gifs/perro.mp4')
            elif "cookie añade" in update.message.text.lower():
                videoTitle = update.message.text.lower().replace("cookie añade ", "")

                if censorYoutubeVideo(videoTitle):
                    update.message.reply_text(
                        'No. :)', reply_to_message_id=update.message.message_id)
                else:
                    connectToSpotifyAndCheckAPI(update, videoTitle, [], None)
            elif re.search(r'\bcabra\b', update.message.text.lower()):
                randomValue = getRandomByValue(4)
                if randomValue <= 1:
                    sendGif(bot, update, dataPath + '/gifs/cabra_scream.mp4')
            elif unidecode(u'qué?') == unidecode(update.message.text.lower()) or "que?" == update.message.text.lower():
                sendGif(bot, update, dataPath + '/gifs/cabra.mp4')
            elif unidecode(u'aió') == unidecode(update.message.text.lower()) or re.search(r'\baio\b', update.message.text.lower()):
                sendGif(bot, update, dataPath + '/gifs/bye.mp4')
            elif re.search(r'\breviento\b', update.message.text.lower()) or re.search(r'\brebiento\b', update.message.text.lower()):
                sendGif(bot, update, dataPath + '/gifs/acho_reviento.mp4')
            elif re.search(r'\bchoca\b', update.message.text.lower()):
                sendGif(bot, update, dataPath + '/gifs/choca.mp4')
            elif re.search(r'\bbro\b', update.message.text.lower()):
                sendGif(bot, update, dataPath + '/gifs/cat_bro.mp4')
            elif "templo" in update.message.text.lower() or "gimnasio" in update.message.text.lower():
                randomValue = getRandomByValue(4)
                if randomValue <= 1:
                    sendGif(bot, update, dataPath + '/gifs/templo.mp4')
            elif re.search(r'\bhuehue[hue]+\b', update.message.text.lower()):
                randomHuehuehueIndex = getRandomByValue(len(huehuehuePath) - 1)
                sendGif(bot, update, dataPath +
                        huehuehuePath[randomHuehuehueIndex])

            # messages
            elif "cookie dame la lista" in update.message.text.lower():
                gimmeTheSpotifyPlaylistLink(bot, update)
            elif "cookie dame la config" in update.message.text.lower():
                bot.send_document(chat_id=update.message.chat_id, document=open(
                    os.path.join(os.path.dirname(__file__)) + '/data_cookie.json', 'rb'))
                bot.send_document(chat_id=update.message.chat_id, document=open(
                    os.path.join(os.path.dirname(__file__)) + '/config.ini', 'rb'))
            elif re.search(r'\bdios\b', update.message.text.lower()):
                randomValue = getRandomByValue(4)
                if randomValue < 1:
                    indexMsg = getRandomByValue(len(random4GodMsg) - 1)
                    update.message.reply_text(
                        random4GodMsg[indexMsg], reply_to_message_id=update.message.message_id)

            # imgs

            # stickers
            elif len(update.message.text) > 4:  # mimimimimimi
                randomResponse(update, bot)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def callback_andalucia(bot, job):
    bot.send_message(chat_id=job.context, text="¡Buenoh díah, Andalucía! :D")


def callback_bye(bot, job):
    bot.send_message(chat_id=job.context, text="AIÓ")
    bot.sendChatAction(chat_id=job.context,
                       action=telegram.ChatAction.UPLOAD_PHOTO)
    bot.sendDocument(chat_id=job.context, document=open(
        dataPath + '/gifs/bye.mp4', 'rb'))


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
