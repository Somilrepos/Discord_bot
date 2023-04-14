import discord
import openai
from yt_dlp import YoutubeDL
import time
from discord.ext import tasks

global vc
reminders = {}

openai.api_key = "TOKEN"

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
client = discord.Client(intents = intents)

client.run("TOKEN")

# Checks the set reminders.
@tasks.loop(minutes=1)
async def check_function():
    cur_tm = int(time.time())
    for tm in reminders:
        if abs(cur_tm-tm) in range(0,60):
            msg = " ".join(reminders[tm].content.split()[2:])
            await reminders[tm].channel.send(f"Hey {reminders[tm].author}, {msg}")


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    check_function.start()


@client.event
async def on_message(message):
    
    # Ingores the messages by the bot itself.
    if message.author == client.user:
        return
    
    # Converts the text message into lower case letter.
    temp_message = message.content.lower()
    
    if temp_message.startswith("$connect"):
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}
        YDL_OPTIONS = {
        'format': 'bestaudio',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }
        search = " ".join(temp_message.split()[1:])
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{str(search)}",download=False)['entries'][0]
        source = info['url']
        await message.channel.send("Connected!")           
        audio = discord.FFmpegPCMAudio(source,**FFMPEG_OPTIONS,executable="C:/Program Files/ffmpeg/bin/ffmpeg.exe",)
        guild = client.get_guild(YOUR_GUILD_ID)
        voice_chnl = await guild.create_voice_channel(name = f'{search} - music')
        voice_protocol = await voice_chnl.connect()
        voice_protocol.play(audio)
        vc = voice_protocol
        
    # Pauses music   
    elif temp_message.startswith("$pause"):
        if vc:
          vc.pause()
        else:
          message.channel.send("There is no music playing.")
    
    # Resumes music
    elif temp_message.startswith("$resume"):
        if vc:
          vc.resume()
        else:
          message.channel.send("There is no music playing.")
          
    # Help response
    elif temp_message.startswith("$reminder"):
        reminders[int(time.time()) + 60*int(temp_message.split()[1])] = message

    elif temp_message.startswith("$help"):
        await message.channel.send("Hey so you asked for help.\n\nHere just use '$' symbol before your question to have ChatGPT3 reply to it.")
        
    # Helps to chat with open ai.
    elif temp_message.startswith("$"):
        response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"you are a discord chatbot so behave like one and respond to this in a humanly manner:\n\n{message.content[1:]}",
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
        )
        response = response['choices'][0]['text'][response['choices'][0]['text'].find('\n')+2:]
        await message.channel.send(response)
