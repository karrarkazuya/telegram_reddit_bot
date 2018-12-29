#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auther: Karrar S. Honi
Date: 12/29/2018
"""
import logging
import telegram
import json
import requests
from telegram.error import NetworkError, Unauthorized
from time import sleep

# Bot config
# Bot token used to connect
TOKEN = ""
# Channel where the bot will post in
CHANNEL = "@tele_food"
# The name of the file the posts to be recorded in, for preventing duplicated posts
POSTED_FILE = "posted_images.txt"
# The name of the file used to log what happens
LOG_FILE = "log.txt"
# Borads of reddit the bot will take posts from
REDDIT_BOARD = ["FoodPorn", "streetfoodartists", "Baking"]
################################################################################
def main():
    print("Running the bot version 1.0")
    global TOKEN
    global POSTED_FILE
    global LOG_FILE
    global REDDIT_BOARD
    global CHANNEL
    print("Posting to "+CHANNEL)
    # Telegram Bot Authorization Token
    bot = telegram.Bot(TOKEN)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # An infinity loop for making it run infinitely
    while True:
        try:
            start(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            print("A removed/blocked bot")

"""
Used to write to the log
"""
def log(text):
    print(text)
    with open(LOG_FILE, "a") as text_file:
        text_file.write(text + "\n")

"""
Used to write to the posted file to prevent duplicated posts
"""
def setPosted(image):
    with open(POSTED_FILE, "a") as text_file:
        text_file.write(image + "\n")

"""
Remove unwanted tags from the title of the post
"""
def pureTitle(text):
    if "[" in text and "]" in text:
        f = text.index("[")
        l = text.index("]")
        l = l + 1
        toCut = text[f:l]
        text = text.replace(toCut, "")
    return text

"""
To start the bot service
"""
def start(bot):
    try:
        for BOARD in REDDIT_BOARD:
            content = requests.get("https://www.reddit.com/r/pics/search.json?q="+BOARD+"&sort=new")
            data = json.loads(content.content)
            image = ""
            try:
                data = data.get("data")
                children = data.get("children")
                for item in children:
                    pass_post = False
                    item = item.get("data")
                    image = item.get("url")
                    title = item.get("title")
                    title = pureTitle(title)
                    with open(POSTED_FILE, "r") as ins:
                        for line in ins:
                            if image in line:
                                pass_post = True
                                break
                    if pass_post:
                        continue
                    if "https://www.reddit.com/r/" not in image:
                        if "https://www.youtube.com/watch" not in image and "https://imgur.com/" not in image:
                            bot.sendPhoto(CHANNEL, image, title)
                        else:
                            bot.sendMessage(CHANNEL,title+"\n"+image)
                        log("posted: "+image)
                    else:
                        log("Skipping link")
                    setPosted(image)
                    sleep(5)
            except Exception as e:
                if image != "":
                    setPosted(image)
                    log("Error at image: "+image)
                    log("Error: "+str(e))
                    log("Skipping")
            
            sleep(5)
    except Exception as e:
        if image != "":
            setPosted(image)
        log("Error: Network error")
        sleep(25)


if __name__ == '__main__':
    main()
