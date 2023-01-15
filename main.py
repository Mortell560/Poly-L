import discord
from discord.ext import commands
from discord.ext import tasks
from discord.utils import find
from grades import getGrades
from utils import *
import interactions

js = import_params_from_json('params.json')
TOKEN = js['token']
PREFIX = js['prefix']
OWNER = js['owner']
ID = js['studentID']
PASSWORD = js['password']

students_edt = {}
server_grade_channels = []


intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, owner_id=OWNER)

@tasks.loop(minutes=30)
async def grades():
    grades = getGrades(ID, PASSWORD)

    ### Polytech
    guild = find(lambda g: 'PEIP' in g.name, bot.guilds)
    channel = find(lambda c: 'nouvelles-notes' in c.name, guild.text_channels)

    messages = await channel.history(limit=None).flatten()

    
    ### New Grades
    previousGrades = [
        message.embeds[0].footer.text
        for message in messages
        if len(message.embeds)
        and message.embeds[0].title.startswith('Nouvelle note')
    ]
    
    newGrades = [
        grade for grade in grades
        if not f"{grade['subject-id']} - {grade['name']}" in previousGrades
        and grade['grade'] is not None
    ]
    
    if len(newGrades):
        await channel.send('||@everyone||')
    
    for grade in newGrades:
        embed = discord.Embed(
            title=f"Nouvelle note en **{grade['subject']}** !",
            color=0x00A8E8,
            url='https://oasis.polytech.universite-paris-saclay.fr/',
            description=grade['name'],
            timestamp=grade['date'],
        )

        oasis_icon = 'https://oasis.polytech.universite-paris-saclay.fr/prod/bo/picture/favicon/polytech_paris_oasis/favicon-194x194.png'
        embed.set_thumbnail(oasis_icon)
        embed.set_footer(text = f"{grade['subject-id']} - {grade['name']}")

        await channel.send(embed=embed)
        print(f"{grade['subject-id']} - {grade['name']}")
    
    
    ### Pending grades
    previousPendingGrades = [
        message.embeds[0].footer.text
        for message in messages
        if len(message.embeds)
        and 'bientôt' in message.embeds[0].title.lower()
    ]
    
    newPendingGrades = [
        grade for grade in grades
        if not f"{grade['subject-id']} - {grade['name']}" in previousPendingGrades
        and grade['grade'] is None
    ]

    for grade in newPendingGrades:
        embed = discord.Embed(
            title=f"*Une note devrait bientôt être disponible en **{grade['subject']}***  👀",
            color=0x00A8E8,
            url='https://oasis.polytech.universite-paris-saclay.fr/',
            description=grade['name'],
            timestamp=grade['date'],
        )
        embed.set_footer(text = f"{grade['subject-id']} - {grade['name']}")

        await channel.send(embed=embed)
        print(f"[ SOON ] {grade['subject-id']} - {grade['name']}")

@tasks.loop(minutes=20)
async def edt_newsletter():
    pass

@bot.command(name='AddNewsletter')
async def add_student_to_newsletter(ctx, id: int):
    pass

@bot.command(name='AddChannel')
@commands.has_permissions(discord.Permissions.administrator)
async def add_server_to_newsletter(ctx):
    pass

@bot.event
async def on_ready():
    print('Gentlemen')
    bot.change_presence(activity=discord.Game(name='with your soul'))
    grades.start()
    edt_newsletter.start()
    print('Mentlegen')

if __name__ == '__main__':
    bot.run(TOKEN)