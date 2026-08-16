import discord
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_SERVER = os.getenv("DISCORD_SERVER_NAME")

intents = discord.Intents.default()
d_cl = discord.Client(intents=intents)
discord_loop = None

@d_cl.event
async def on_ready():
    global discord_loop
    discord_loop = asyncio.get_event_loop()
    
    print(f"{d_cl.user} has connected")

async def upload_file(filename:str, file_hex:str):
    chan = discord.utils.get(d_cl.get_all_channels(), name="files")

    await chan.send(f"{filename}\n\n{file_hex}")

async def get_files_list() -> list[str]:
    chan = discord.utils.get(d_cl.get_all_channels(), name="files")
    files_list:list[str] = []

    async for msg in chan.history(limit=None, oldest_first=False):
        fname = str(msg.content).split("\n\n")[0].split(":")[0]
        if fname not in [i.split(":")[0] for i in files_list]:
            files_list.append(
                f"{fname}:{msg.id}"
            )

    return files_list

async def download_file(filename:str, file_id:str) -> str:
    chan = discord.utils.get(d_cl.get_all_channels(), name="files")
    og_msg = await chan.fetch_message(int(file_id))
    print("download part", og_msg.content)
    file_hex:str = og_msg.content.split("\n\n")[1]

    async for msg in chan.history(before=discord.Object(id=int(file_id)), limit=None):
        try:
            c = msg.content.split("\n\n")[1]
            print("download part", msg.content.split("\n\n")[0].split(":")[1])
            file_hex = f"{c}{file_hex}"
            if msg.content.split("\n\n")[0].split(":")[0] != filename:
                print(msg.content.split("\n\n")[0].split(":")[0], "wasnt equal to", filename)
                break
        except Exception as e:
            continue

    return file_hex

def run_bot():
    d_cl.run(DISCORD_TOKEN)