import asyncio
import glob
import os
from os import path
import platform
import discord
import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip, ImageClip
import logging
import re
from optionshandler import options
from discord.ext import commands
import asyncio


# maybe needed later for hyper threading (if the current model doesn't work)
# import functools
# import typing
# def to_thread(func: typing.Callable) -> typing.Coroutine:
#     @functools.wraps(func)
#     async def wrapper(*args, **kwargs):
#         def funcy():
#             client.loop.create_task(func(*args,**kwargs))
#         return await asyncio.to_thread(funcy)
#     return wrapper


print("Listens with prefix: ", options.prefix)

__version__ = '2.0'

ller = "\\"
if platform.system() == "Linux":
    ller = "/"

home_path = os.getcwd()
tmp_path = f'{home_path}{ller}tmp{ller}'

acceptable_audio_files = (".mp3", ".wav", ".flac", ".ogg", ".m4a")

# create data folder if it doesn't exist
if path.exists(tmp_path) == False:
    os.mkdir(tmp_path)

os.chdir(home_path)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

intents = discord.Intents.default()
intents.typing = False  # Disable typing events
intents.presences = False  # Disable presence events
intents.messages = True  # Enable message events
intents.message_content = True  # Enable message content in message events
intents.guilds = True  # Enable guild events

client = commands.Bot(command_prefix=options.prefix, intents=intents)


async def create_image_with_text(text, output= f'{tmp_path}output.png'):
    try:
        font_path = f'{home_path}{ller}fonts{ller}framd.ttf'
        BG_COLOR = (88, 101, 243)  # discord purple color
        IMG_DIMENSIONS = (260, 60)

        font_size = 42 - len(text)
        if font_size < 10:
            font_size = 10

        fnt = ImageFont.truetype(font_path, font_size)
        fnt_sm = ImageFont.truetype(font_path, 10)

        img = Image.new('RGB', IMG_DIMENSIONS, color=BG_COLOR)

        d = ImageDraw.Draw(img)
        d.text((img.size[0]//2, img.size[1]//2), text, anchor='mm', font=fnt, fill=(255, 255, 255))
        d.text((IMG_DIMENSIONS[0]-90, IMG_DIMENSIONS[1]-13), 'Audio Reposter v2', font=fnt_sm, fill=(170, 170, 170))

        img.save(output)

        return output
    except Exception as e:
        logger.error(f"Error in create_image_with_text: {e}")


async def convert_audio_to_video(audio_input, filename, unique_id, output='output.mp4'):
    try:
        img_path = await create_image_with_text(filename, f'{tmp_path}{unique_id}.png')
        audioclip = AudioFileClip(audio_input)
        imgclip = ImageClip(img_path)
        imgclip = imgclip.set_duration(audioclip.duration)
        videoclip = imgclip.set_audio(audioclip)
        video_codec = 'libx264'
        audio_codec = 'aac'
        audio_bitrate = '384k'
        video_bitrate = '128k'
        videoclip.write_videofile(
            output,
            codec=video_codec,
            audio_codec=audio_codec,
            audio_bitrate=audio_bitrate,
            bitrate=video_bitrate,
            logger=None,
            fps=1
        )
        videoclip.close()
    except Exception as e:
        logger.error(f"Error in convert_audio_to_video: {e}")


async def send_test_message(guild):
    try:
        thread_id = 1121381041396002826
        thread = guild.get_channel_or_thread(thread_id)
        if thread:
            await thread.send("Test message sent!")
        else:
            print(f"Error: Thread with ID {thread_id} not found in the guild.")
    except discord.Forbidden:
        print(f"Error: Bot does not have permission to send messages in {thread.name}")
    except discord.HTTPException as e:
        print(f"Error: Failed to send test message in {thread.name}. {e}")
    except Exception as e:
        logger.error(f"Error in send_test_message: {e}")

async def send_message_to_all_channels(guild):
    message = "This bot was not designed for other servers to use, and may be laggy since we prioritize AI HUB. " \
              "If you would like to support the bot to be published in more servers, please donate $1 a month or " \
              "more to help pay for a better hosting provider. It is currently overloaded by a hundred servers " \
              "using it since it is on just one $4 server. [Donate Here](https://ko-fi.com/kalomaze)"

    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel):
            await channel.send(message)


def save_profile_picture(user):
    try:
        pfp_url = user.avatar.url
        response = requests.get(pfp_url)
        if response.status_code == 200:
            with open(f'{tmp_path}pfp.png', 'wb') as f:
                f.write(response.content)
            print("Profile picture saved as pfp.png")
        else:
            print("Failed to save profile picture")
    except Exception as e:
        logger.error(f"Error in save_profile_picture: {e}")



async def aio_all(seq):
  for f in asyncio.as_completed(seq):
    await f

# @to_thread
async def handle_file(file, message: discord.message.Message, index=0):
    file_name = file.filename if isinstance(file, discord.Attachment) else "audio_file.mp3"
    unique_id = f'{str(index)}_{str(message.guild.id)}_{str(message.channel.id)}_{str(message.id)}_{str(message.author.id)}'
    try:
        if isinstance(file, str) or file.filename.lower().endswith(acceptable_audio_files):
            async with message.channel.typing():
                audio_file_path = await download_file(file, f'{unique_id}.{file_name[:10].split(".")[-1]}')
                await convert_and_send_video(audio_file_path, file_name, unique_id, message)
                await removeBolk(unique_id)
    except Exception as e:
        logger.error(f"Error in handle_file: {e}")


def has_role(message: discord.message.Message, role_id: str):
    does = False
    for rl in message.author.roles:
        if str(rl.id) == role_id:
            does= True
    return does
        


@client.event
async def on_message(message: discord.message.Message, timesIn=0):
    try:
        if message.author.bot:
            return
        
        await client.process_commands(message)

        files_to_download = []
        if len(message.attachments) > 0:
            files_to_download = message.attachments
        elif message.content:
            files_to_download = get_audio_urls(message.content)
            
        if len(files_to_download) > 0:
            asyncio.run_coroutine_threadsafe(aio_all([handle_file(file, message, inx) for inx, file in enumerate(files_to_download)]), client.loop)
    except Exception as e:
        logger.error(f"Error in on_message: {e}")

def get_audio_urls(content):
    # Split the input string into words
    words = content.split()
    # List to store extracted URLs
    urls = []

    for word in words:
        # Check if the word contains a URL-like pattern
        match = re.match(r'^(https?://[^\s/$.?#]+(?:\.[^\s]*)?)(?:[.,]?[\s]|$)', word, re.IGNORECASE)
        if match:
            url = match.group(1)
            # Check if the URL ends with "," or "."
            if url.endswith((',', '.')):
                url = url[:-1]  # Remove the trailing character
            if url.lower().endswith(acceptable_audio_files):
                urls.append(url)

    return urls

async def download_file(file, customName):
    try:
        file_name = file.filename if isinstance(file, discord.Attachment) else "audio_file.mp3"
        
        if customName:
            file_name = customName
            
        file_path = f'{tmp_path}{file_name}'

        # print(f"Downloading: {file.filename if isinstance(file, discord.Attachment) else file}")
        url = file.url if isinstance(file, discord.Attachment) else file
        with open(file_path, 'wb') as f:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            block_size = 1024
            for data in response.iter_content(block_size):
                downloaded_size += len(data)
                f.write(data)
        # print("Download completed.")
        return file_path
    except Exception as e:
        logger.error(f"Error in download_file: {e}")

async def convert_and_send_video(audio_file_path, file_name, unique_id, message):
    try:
        video_file_path = f'{tmp_path}{unique_id}.mp4'

        await convert_audio_to_video(audio_file_path, file_name, unique_id, video_file_path)
        # print("Uploading video...")
        await message.channel.send(file=discord.File(video_file_path), reference=message)
        print("Upload completed.", unique_id, ".mp4" )
    except Exception as e:
        logger.error(f"Error in convert_and_send_video: {e}")


async def removeBolk(id):
    try:
        # get a recursive list of file paths that matches pattern including sub directories
        fileList = glob.glob(f'{tmp_path}{id}.*', recursive=True)

        # Iterate over the list of filepaths & remove each file.
        for filePath in fileList:
            try:
                os.remove(filePath)
            except OSError:
                print("Error while deleting file", filePath)
    except Exception as e:
        logger.error(f"Error in removeBolk: {e}")



@client.command(name="@")
async def mobile(ctx: commands.context.Context):
    message = ctx.message
    
    full_id = f'{str(message.guild.id)}_{str(message.channel.id)}_{str(message.author.id)}'

    if not message.reference:
        return
    
    ref_message = message.reference.resolved
        
    # print('Message:', message.content)
    # print('Attachments:', len(message.attachments))
    # if the user uses command to generate 
    if ref_message:
        do_it = False
        if len(options.allowed) == 0:
            do_it = True
        else:
            for alm in options.allowed:
                rej, role_id, comment = alm.split("__")
                if len(rej) > 0 and len(role_id) > 0 and re.match(re.escape(rej), full_id) and has_role(message.author.roles, role_id):
                    do_it = True
                elif len(rej) > 0 and re.match(re.escape(rej), full_id):
                    do_it = True
                elif len(role_id) > 0 and has_role(message, role_id) :
                    do_it = True

        if not ref_message.attachments and len(get_audio_urls(ref_message.content)) == 0:
            do_it = False

        if do_it:
            try:
                await message.delete()
            except:
                print("already deleted")
            await ctx.typing()
            await on_message(ref_message)
        return
    
@client.command(name="!")
async def help(ctx: commands.context.Context):
    sent_message = await ctx.send(f"HI dis is the help aaa...")
    await asyncio.sleep(1)
    sent_message = await sent_message.edit(content=f"HI dis is the help aaa... help?")
    await asyncio.sleep(1)
    sent_message = await sent_message.edit(content=f"sry bout dat")
    await asyncio.sleep(1)
    sent_message = await sent_message.edit(content=f"# help:\n## {options.prefix}@ + reply:\n trigger me to repost the audio from the referenced message \n## {options.prefix}ping:\n tell you if i'm available \n## {options.prefix}!:\n aaaa.. to show this message again?")
   
@client.command(name="ping")
async def mobile(ctx: commands.context.Context):
    await ctx.send(f"I'm ALIVE PLEASE DON't REBOOT ME, '{options.prefix}help' for commands info")

@client.tree.command()
async def mobile(ctx):
    message = ctx.message

    full_id = f'{str(message.guild.id)}_{str(message.channel.id)}_{str(message.author.id)}'
        
    # print('Message:', message.content)
    # print('Attachments:', len(message.attachments))
    # if the user uses command to generate 
    if message.reference.resolved:
        do_it = False
        if len(options.allowed) == 0:
            do_it = True
        else:
            for alm in options.allowed:
                rej, role_id, comment = alm.split("__")
                if len(rej) > 0 and len(role_id) > 0 and re.match(re.escape(rej), full_id) and has_role(message.author.roles, role_id):
                    do_it = True
                elif len(rej) > 0 and re.match(re.escape(rej), full_id):
                    do_it = True
                elif len(role_id) > 0 and has_role(message, role_id) :
                    do_it = True

        if do_it:
            await on_message(message.reference.resolved)
        return



@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    guilds = client.guilds

    with open(f"{tmp_path}servers.txt", "w") as file:
        for guild in guilds:
            file.write(f"Server Name: {guild.name}\n")
            file.write(f"Server ID: {guild.id}\n")
            client.tree.clear_commands(guild=discord.Object(id=guild.id))
            await client.tree.sync(guild=discord.Object(id=guild.id))

            try:
                invites = await guild.invites()
                file.write("Invites:\n")
                for invite in invites:
                    file.write(f"- {invite.url}\n")
            except discord.Forbidden:
                file.write("Error: Could not access invites\n")

            file.write("Accessible Channels:\n")
            for channel in guild.channels:
                if channel.permissions_for(guild.me).send_messages:
                    if channel.permissions_for(guild.default_role).manage_messages:
                        file.write(f"- Channel Name: {channel.name} (ID: {channel.id}) - Bot can post, and it's a moderator only channel\n")
                    else:
                        file.write(f"- Channel Name: {channel.name} (ID: {channel.id}) - Bot can post, and it's not a moderator only channel\n")
                else:
                    if channel.permissions_for(guild.default_role).manage_messages:
                        file.write(f"- Channel Name: {channel.name} (ID: {channel.id}) - Bot can't post, and it's a moderator only channel\n")
                    else:
                        file.write(f"- Channel Name: {channel.name} (ID: {channel.id}) - Bot can't post, and it's not a moderator only channel\n")

            file.write("Roles:\n")
            for role in guild.roles:
                file.write(f"- {role.name}\n")

    print("Server information saved to servers.txt")
    


# Properly handle exceptions and log errors in the main function
def main():
    try:
        client.run(TOKEN)
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()

