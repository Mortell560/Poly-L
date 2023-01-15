import discord
from discord.ext import commands
from discord.ext import tasks
from discord.utils import find
from utils import *
import interactions

js = import_params_from_json('params.json')
TOKEN = js['token']
PREFIX = js['prefix']
OWNER = js['owner']


intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, owner_id=OWNER)

@tasks.loop(minutes=30)
async def grades():
    pass

@tasks.loop(minutes=20)
async def edt():
    pass


@bot.event
async def on_ready():
    print('Gentlemen')
    bot.change_presence(activity=discord.Game(name='with your soul'))
    grades.start()
    edt.start()
    print('Mentlegen')

if __name__ == '__main__':
    bot.run(TOKEN)