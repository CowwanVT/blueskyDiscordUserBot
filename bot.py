import requests
import json
from datetime import datetime, timezone
import discord
from discord.ext import tasks

profile = '' #profile to scrape from
requestURL = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed'
limit = 10 #how many posts back to check
postFilter = 'posts_no_replies' #which posts to grab, can be posts_with_replies, posts_no_replies, posts_with_media, posts_and_author_threads
includePins = 'False' #whether or not to grab pinned posts

discordChannelID = #channel ID to post in
discordBotToken = #bot token from discord developer

interval = 15 #how many minutes to wait between checks


global lastUpdateTime
lastUpdateTime = datetime.now(timezone.utc).timestamp()

def getBlueskyPosts():
    constructedURL = requestURL + '?actor=' + profile + '&limit=' + str(limit) + '&filter='+ postFilter + '&includePins=' + includePins
    response = requests.get(constructedURL).json()
    return response

intents = discord.Intents.default()

intents.message_content = True
client = discord.Client(intents=intents)

@tasks.loop(minutes = interval)
async def checkPosts():
    global lastUpdateTime

    await client.wait_until_ready()
    channel = client.get_channel(discordChannelID)
    response = getBlueskyPosts()
    for post in response['feed']:

        postTime = datetime.strptime(post['post']['record']['createdAt'],  '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()

        if postTime > (lastUpdateTime):
            postURL = 'https://bsky.app/profile/'+ post['post']['author']['handle'] + '/post/' + post['post']['uri'].split('/')[4]
            await channel.send(postURL)
    lastUpdateTime = datetime.now().timestamp()- 20

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    checkPosts.start()

client.run(discordBotToken)
