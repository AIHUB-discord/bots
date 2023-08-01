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

is_script_going = False

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

client = discord.Client(intents=intents)


def create_image_with_text(text, output= f'{tmp_path}output.png'):
    try:
        font_path = f'{home_path}{ller}fonts{ller}framd.ttf'
        print("font_path", font_path)
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


def convert_audio_to_video(audio_input, filename, unique_id, output='output.mp4'):
    try:
        img_path = create_image_with_text(filename, f'{tmp_path}{unique_id}.png')
        audioclip = AudioFileClip(audio_input)
        imgclip = ImageClip(img_path)
        imgclip = imgclip.set_duration(audioclip.duration)
        videoclip = imgclip.set_audio(audioclip)
        video_codec = 'libx264'
        audio_codec = 'aac'
        audio_bitrate = '192k'
        video_bitrate = '100k'
        videoclip.write_videofile(
            output,
            codec=video_codec,
            audio_codec=audio_codec,
            audio_bitrate=audio_bitrate,
            bitrate=video_bitrate,
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

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    guilds = client.guilds

    with open(f"{tmp_path}servers.txt", "w") as file:
        for guild in guilds:
            file.write(f"Server Name: {guild.name}\n")
            file.write(f"Server ID: {guild.id}\n")

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

async def handle_file(file, message: discord.message):
    unique_id = f'{file.filename}_{str(message.channel.id)}_{str(message.id)}_{str(message.author.id)}'
    try:
        if isinstance(file, str) or file.filename.lower().endswith(acceptable_audio_files):
            audio_file_path = await download_file(file, f'{unique_id}.{file.filename.split(".")[-1]}')
            await convert_and_send_video(audio_file_path, file.filename, unique_id, message)

            removeBolk(unique_id)
    except Exception as e:
        logger.error(f"Error in handle_file: {e}")


@client.event
async def on_message(message: discord.message):
    try:
        # print('Message:', message.content)
        # print('Attachments:', len(message.attachments))
        global is_script_going
        files_to_download = []
        if message.attachments:
            files_to_download = message.attachments
        elif message.content:
            files_to_download = get_audio_urls(message.content)
            
        if not is_script_going:
            is_script_going = True
            await aio_all([handle_file(file, message) for file in files_to_download])
            is_script_going = False
    except Exception as e:
        logger.error(f"Error in on_message: {e}")

def get_audio_urls(content):
    return [word for word in content.split() if any(ext in word.lower() for ext in acceptable_audio_files)]

async def download_file(file, customName):
    try:
        file_name = file.filename if isinstance(file, discord.Attachment) else "audio_file.mp3"
        
        if customName:
            file_name = customName
            
        file_path = f'{tmp_path}{file_name}'

        print(f"Downloading: {file.filename if isinstance(file, discord.Attachment) else file}")
        url = file.url if isinstance(file, discord.Attachment) else file
        with open(file_path, 'wb') as f:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            block_size = 1024
            for data in response.iter_content(block_size):
                downloaded_size += len(data)
                f.write(data)
        print("Download completed.")
        return file_path
    except Exception as e:
        logger.error(f"Error in download_file: {e}")

async def convert_and_send_video(audio_file_path, file_name, unique_id, message):
    try:
        video_file_path = f'{tmp_path}{unique_id}.mp4'

        convert_audio_to_video(audio_file_path, file_name, unique_id, video_file_path)
        print("Uploading video...")
        await message.channel.send(file=discord.File(video_file_path), reference=message)
        print("Upload completed.")
        is_script_going = False
    except Exception as e:
        logger.error(f"Error in convert_and_send_video: {e}")


def removeBolk(id):
    # get a recursive list of file paths that matches pattern including sub directories
    fileList = glob.glob(f'{tmp_path}{id}.*', recursive=True)

    # Iterate over the list of filepaths & remove each file.
    for filePath in fileList:
        try:
            os.remove(filePath)
        except OSError:
            print("Error while deleting file", filePath)

client.run(TOKEN)
