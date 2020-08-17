import sys, os, socket, json, discord, requests, asyncio, time, twitter
from youtube_dl import YoutubeDL
import bot_tokens
from ytdl import PORT_NUM # import port number for youtube-dl agent

ydl_agent = YoutubeDL() # init youtube-dl agent

_reply = { # Some simple replies for '$' commands
    "$cool" : "story bro",
    "$time" : f'The time is {time.ctime()}',
    "!help" : "help string"
    }
_replykeys = _reply.keys()

_tweet = {
    "!twice" : "jypetwice",
    "!loona" : "loonatheworld",
}
_tweetkeys = _tweet.keys()

# --- twitter api and fetch
twitter = twitter.Api(consumer_key=bot_tokens.consumer_key,
                  consumer_secret=bot_tokens.consumer_secret,
                  access_token_key=bot_tokens.access_token_key,
                  access_token_secret=bot_tokens.access_token_secret)

async def getlasttweet(user):
    try:
        status = twitter.GetUserTimeline(screen_name=user, count=1)
    except Exception as err:
        print(f"[Tweet]: {err}")
        return f"[{user}] user profile is private/does not exist."
    return f"https://twitter.com/{user}/status/{status[0].id}"
# ---


# --- ytdl socket
async def parse_ytdl(video_url):
    try:
        print(f"[YTDL] Parsing video: {video_url}")
        info = ydl_agent.extract_info(video_url, download=False)
        print(f"[YTDL] Valid video: {info['title']}")
    except:
        return "Error parsing video/video not found"
    else:
        if info['duration'] < 600:
            print(f"[YTDL] Sending {info['title']} to youtube-dl")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect(("localhost", PORT_NUM))
                    s.send(video_url.encode())
                except:
                    print("Can not connect to Youtube-dl")
                    return "Can not connect to Youtube-dl"
                else:
                    print(f"'{info['title']}' sent to youtube-dl")
                    return f"'{info['title']}' sent to youtube-dl"
                finally:
                    s.close()

        else:
            print(f"[YTDL] Video {info['title']} longer than allowed duration")
            return "Video longer than allowed duration."        
# ---

# SCP fetch ---
async def get_scp(search):
    base = 'https://crom-dev.avn.sh/search?q='
    response = requests.get(base+search)
    json_obj = json.loads(response.content.decode('utf-8'))
    if 'status' in json_obj.keys() and json_obj['status'] == 404:
        return "SCP not found"
    else:
        tags = ""
        for tag in json_obj['tags']:
            tags += tag+" "
        return f"{json_obj['title']}: {json_obj['scp_title']}\n{json_obj['url']}\nTags: {tags}\n`powered by CROM`"
# ---


class Bot(discord.Client):

    async def on_ready(self):
        print(f"{self.user} Ready")
        for guild in self.guilds:
            print(f'{self.user} connected to {guild.name}')
    
    
    async def on_message(self, message):
        if message.author == self.user:
            return

        elif message.content == "!embedtest":
            msg = discord.Embed(title="An embed!", author="JS bot", description="Description here", color=0x6495ED)
            msg.add_field(name="text1", value="Text block1")
            await message.channel.send(embed=msg)
            
        elif message.content in _tweetkeys:
            print(f'{time.ctime()} [Tweet: {_tweet[message.content]}] Replying to {message.author} in {message.guild}/{message.channel}')
            msg = await getlasttweet(_tweet[message.content])
            await message.channel.send(f"Last tweet from {_tweet[message.content]}:\n"+msg)
            return

        elif message.content.startswith("!tw"):
            if len(message.content.split()) != 2:
                await message.channel.send("`$tw [username]` to get tweet.")
                return
            username = message.content.split()[1]
            print(f'{time.ctime()} [Tweet: {username}] Replying to {message.author} in {message.guild}/{message.channel}')
            msg = await getlasttweet(username)
            await message.channel.send(f"Latest tweet from {username}:\n"+msg)
            return

        elif message.content.startswith("!ytdl"): #TODO add user verification;
            if len(message.content.split()) != 2:
                await message.channel.send("`$ytdl [url]` to download a video.")
                return
            url = message.content.split()[1]
            print(f'{time.ctime()} [YTDL] Replying to {message.author} in {message.guild}/{message.channel}')
            await message.channel.send("YTDL request queued.")
            msg = await parse_ytdl(url)
            await message.channel.send(msg)
            return

        elif message.content.startswith("!scp"):
            if len(message.content.split()) == 1:
                await message.channel.send("`$scp [# or search terms]` to find an SCP article.")
                return
            search = "+".join(message.content.split()[1:])
            print(search)
            print(f'{time.ctime()} [SCP] Replying to {message.author} in {message.guild}/{message.channel}')
            msg = await get_scp(search)
            await message.channel.send(msg)
            return

        elif message.content in _replykeys:
            print(f'{time.ctime()} [Simple] Replying to {message.author} in {message.guild}/{message.channel}')
            await message.channel.send(_reply[message.content])
            return


def main():
    bot = Bot()
    bot.run(bot_tokens.discord_token)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()