#!/usr/bin/env python
# -*- coding: utf-8 -*-

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from .youtubeApi import YoutubeAPI
import json
import os
import re


class SpotifyYouTubeClass:
    settings = {}


    # Save Data song if it didn't find
    def saveDataSong(update, sendMessage):
        data = []
        try:
            json_file = open('data.txt', 'r')
            data = json.load(json_file)
        except IOError:
            data = []

        data.append(update.message.text)
        with open('data.txt', 'w') as outfile:
            json.dump(data, outfile)

        if sendMessage:
            update.message.reply_text(
                "No está. :_(", reply_to_message_id=update.message.message_id)

    # call spotify api to get the songid of spotify with:
    def callSpotifyApi(self, videoTitle, videoTags, video, sp, update):
        try:
            # youtube video title
            results = sp.search(q=videoTitle, limit=1)
            if int(results['tracks']['total']) == 0:
                results = sp.search(q=videoTags, limit=1)
            #youtube video tags
            if int(results['tracks']['total']) == 0 and video != None:
                videoTags = ""
                videoTags = gimmeTags(video, videoTags, 2)
                results = sp.search(q=videoTags, limit=1)
            #youtube video tags same with less tags
            if int(results['tracks']['total']) == 0 and video != None:
                videoTags = ""
                videoTags = gimmeTags(video, videoTags, 1)
                results = sp.search(q=videoTags, limit=1)
            return results
        except:
            self.saveDataSong(update, True)

    @staticmethod
    def gimmeTags(video, videoTags, maxTags):
        tagsIndex = 0
        if video['snippet'].get('tags') != None:
            while tagsIndex < len(video['snippet']['tags']) and tagsIndex < maxTags:
                videoTags += video['snippet']['tags'][tagsIndex] + " "
                tagsIndex += 1
        return videoTags

    def addToSpotifyPlaylist(self, results, update):
        resultTracksList = results['tracks']
        idsToAdd = []

        for j in range(len(results['tracks']['items'])):
            idsToAdd.insert(0, results['tracks']['items'][j]['id'])

        self.callSpotifyApiToAddSong(idsToAdd)

    def callSpotifyApiToAddSong(self, idsToAdd):
        # scope to access to the list and it can modify it
        scope = 'playlist-modify playlist-modify-public user-library-read playlist-modify-private'
        # get the app token with userid, scope, client_id, client_secret and redirect_uri (run a server to show a web to grant access to the app with ur user)
        token = util.prompt_for_user_token(self.settings["spotify"]["spotifyuser"], scope, client_id=self.settings["spotify"]
                                           ["spotifyclientid"], client_secret=self.settings["spotify"]["spotifysecret"], redirect_uri='http://localhost:8000')
        # call to spotify API to save the songid to the list
        sp = spotipy.Spotify(auth=token)
        results = sp.user_playlist_add_tracks(
            self.settings["spotify"]["spotifyuser"], self.settings["spotify"]["spotifyplaylist"], idsToAdd)

    def recommendAGroup(self, update):
        scope = 'playlist-modify playlist-modify-public user-library-read playlist-modify-private'
        token = util.prompt_for_user_token(self.settings["spotify"]["spotifyuser"], scope, client_id=self.settings["spotify"]
                                           ["spotifyclientid"], client_secret=self.settings["spotify"]["spotifysecret"], redirect_uri='http://localhost:8000')
        sp = spotipy.Spotify(auth=token)
        offsetPlaylist = getRandomByValue(0)
        # user_playlist_tracks(user, playlist_id=None, fields=None, limit=100, offset=0, market=None)
        results = sp.user_playlist_tracks(
            self.settings["spotify"]["spotifyuser"], self.settings["spotify"]["spotifyplaylist"], None, 100, offsetPlaylist)
        playlistData = json.dumps(results)
        playlistData = json.loads(playlistData)
        if len(playlistData["items"]) > 0:
            index = getRandomByValue(len(playlistData["items"]) - 1)
            track = playlistData["items"][index]["track"]
            return "Ahí te va " + track["external_urls"]["spotify"]
        else:
            return "BOOM, me salí de la lista :/"

    @staticmethod
    def replaceYouTubeVideoName(videoTitle):
        #replace common words in youtube title video
        videoTitle = re.sub(r'\([\[a-zA-Z :\'0-9\]]+\)', '', videoTitle)
        videoTitle = re.sub(r'\[[\[a-zA-Z :\'0-9\]]+\]', '', videoTitle)
        videoTitle = videoTitle.lower().replace("official video", "")
        videoTitle = videoTitle.lower().replace("official music video", "")
        videoTitle = videoTitle.lower().replace("videoclip oficiai", "")
        videoTitle = videoTitle.lower().replace("video clip oficiai", "")
        videoTitle = videoTitle.lower().replace("videoclip", "")
        videoTitle = videoTitle.lower().replace("\"", "")
        return videoTitle

    def connectToSpotifyAndCheckAPI(self, update, videoTitle, videoTags, video):
        client_credentials_manager = SpotifyClientCredentials(
            client_id=self.settings["spotify"]["spotifyclientid"], client_secret=self.settings["spotify"]["spotifysecret"])
        sp = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager)
        sp.trace = False
        # call spotify to get a list of songs
        results = self.callSpotifyApi(videoTitle, videoTags, video, sp, update)

        if results == None or (results['tracks']['total'] != None and results['tracks']['total'] == 0):
            self.saveDataSong(update, None)
            return False
        else:
            self.addToSpotifyPlaylist(results, update)
            return True

    @staticmethod
    def censorYoutubeVideo(videoTitle):
        json_file = open(os.path.join(os.path.dirname(
            __file__), "../youtubeCensor.json"), 'r')
        youtubeCensorData = json.load(json_file)

        for item in youtubeCensorData:
            if item in videoTitle:
                return True
        return None

    def youtubeLink(self, update):
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
                {'key': self.settings["main"]["youtubeapikey"]})
            video = youtube.get_video_info(videoid)
            videoTitle = video['snippet']['title'].lower()
            videoTitle = self.replaceYouTubeVideoName(videoTitle)

            if self.censorYoutubeVideo(videoTitle):
                update.message.reply_text(
                    '...', reply_to_message_id=update.message.message_id)
            else:
                videoTags = ""
                tagsIndex = 0
                videoTags = gimmeTags(video, videoTags, 3)
                if videoTitle != None and videoTags != None:
                    return self.connectToSpotifyAndCheckAPI(
                        update, videoTitle, videoTags, video)
                else:
                    self.saveDataSong(update, None)
        except:
            self.saveDataSong(update, None)
        return False

    def spotifyLink(self, update):
        try:
            trackid = update.message.text.split("track/")
            trackid = trackid[1].split(" ")
            if "?" in trackid:
                trackid = trackid[1].split("?")
            trackid = trackid[0]
            self.callSpotifyApiToAddSong([trackid])
            return True
        except:
            self.saveDataSong(update, None)
        return False

    def checkYoutubeSpotifyLinks(self, update):
        for i in range(len(update.message.entities)):
            if update.message.entities[i].type == 'url' and ('youtu.be' in update.message.text.lower() or 'youtube.com' in update.message.text.lower()):
                #youtube link in the msg
                return self.youtubeLink(update)
            elif update.message.entities[i].type == 'url' and 'spotify.com' in update.message.text:
                #spotify link in the message
                return self.spotifyLink(update)

    def __init__(self, settings):
        self.settings = settings
