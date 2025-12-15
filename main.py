# NOTE: You need to have your keyboard and mouse focused on the QIP window at All times for this to work properly.
# Setup: `pip install pyautogui discord.py watchdog`

import discord, discord.ext, asyncio, pyautogui, time, os
from discord.ext import commands
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

bot_token = ""
qip_path = "C:\\Users\\Admin\\AppData\\Local\\QIP\\QIP 2005\\Users\\100000\\History" # Replace "100000" with your ID
channel_id = 1234567890987654321 # Replace with the id of the channel you are going to use
target_icq_id = 200000
icq_nickname = "nick name"
chat = (f"{qip_path}\\{target_icq_id}.txt")
last_chat_size = os.path.getsize(chat)

class WatchHandler(FileSystemEventHandler):

    def on_modified(self, event):
        global last_chat_size

        if event.src_path == chat: # This part is stolen from ChatGPT since i couldn't find a proper answer for "How to get newly added lines from modified file Watchdog"
                new_chat_size = os.path.getsize(chat)
                if new_chat_size > last_chat_size:
                    with open(event.src_path) as chatlog:
                        chatlog.seek(last_chat_size + 40) # + 40 is there to get rid of the separators at the beggining of each message in the log file
                        msg_icq = chatlog.read()
                        msg_icq_split = msg_icq.split("\n")
                        last_chat_size = new_chat_size
                        if msg_icq_split[1].startswith(icq_nickname): # Weird check i know but it works.
                            return
                        else:
                            SendMsg2Discord(msg_icq)

        if event.src_path == f"{qip_path}/_srvlog.txt":
            with open(event.src_path) as srvlog:
                visibility = (srvlog.readlines() [-3:-1])[1]
                if str(target_icq_id) in visibility:
                    SendMsg2Discord(visibility)

discord_intents = discord.Intents.default()
discord_intents.message_content = True
discord_intents.messages = True
bot = commands.Bot(command_prefix = "!", intents = discord_intents)

def SendMsg2Discord(msg: str):
    bot.loop.create_task((bot.get_channel(int(channel_id))).send(msg))

@bot.event
async def on_message(message: discord.Message):
    if message.channel.id == channel_id:
        if message.author == bot.user: return
        if message.mentions is not None:
            for user in message.mentions:
                message.content = message.content.replace(f"<@{user.id}>", f"@{user.display_name}")
        if message.attachments:
            message.content = message.content + "\n(This message contains an attachment)"
        if message.reference is not None:
            msg = f"{message.author.display_name} ({message.author.name}) (Discord)\n>> {message.reference.resolved.content}\n{message.content}"
        else:
            msg = f"{message.author.display_name} ({message.author.name}) (Discord)\n{message.content}"
        pyautogui.write(msg)
        pyautogui.hotkey("ctrl", "enter")
    else:
        return

watchdog_observer = Observer()
watchdog_handler = WatchHandler()
watchdog_observer.schedule(watchdog_handler, qip_path)
watchdog_observer.start()

bot.run(bot_token)
