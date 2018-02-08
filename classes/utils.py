#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
from random import randint
from datetime import datetime, timedelta


class Utils:

    @staticmethod
    def getRandomByValue(value):
        # get random value to 0 <= value
        randomValue = randint(0, value)
        return randomValue

    @staticmethod
    def loadFile(fileName, isOrdered, errorInit):
        data = {}
        try:
            if isOrdered:
                json_file = open(fileName, 'r')
                data = json.load(json_file, object_pairs_hook=OrderedDict)
            else:
                json_file = open(fileName, encoding="utf-8")
                data = json.load(json_file)
                data = json.dumps(
                    {'data': data})
                data = json.loads(data)
                data = data["data"]
        except IOError:
            data = errorInit
        return data

    @staticmethod
    def saveFile(fileName, fileData):
        with open(fileName, 'w') as outfile:
            json.dump(fileData, outfile)

    @staticmethod
    def replaceStr(msg, str):
        # remove the first (or selected number) occurrence of str and a empty space
        if str in msg:
            msg = msg.replace(str + " ", "", 1)
        return msg

    # set the right datetime to remember by weekday and/or hh:mm dataParsed
    @staticmethod
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
