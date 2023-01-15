import discord
from discord.ext import commands
from discord.ext import tasks
from discord.utils import find
from grades import getGrades
from utils import *
import datetime
import pprint
from deepdiff import DeepDiff
from edt import getEDT, nextClass, findCurrentlyOccupiedRooms
import interactions

js = import_params_from_json('params.json')
TOKEN = js['token']
PREFIX = js['prefix']
ID = js['studentID']
PASSWORD = js['password']

students_edt = {}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, case_insensitive=True)

"""
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
"""

@tasks.loop(minutes=20)
async def edt_newsletter():
    for student, curr_edt in students_edt.items():
        id, discordID = student
        new_edt = getEDT(id=id, dateS=datetime.date(2022, 9, 5), dateF=datetime.date(2023, 7, 24))
        if len(new_edt.events) - len(curr_edt.events):
            students_edt[student] = new_edt
            user = await bot.fetch_user(discordID)
            if user.dm_channel is None:
                await user.create_dm()
            c = user.dm_channel
            changes = list(new_edt.events - curr_edt.events)
            desc = ''
            for change in changes:
                desc += f"**{change.name}**\n"
                desc += f"{change.begin.__add__(datetime.timedelta(hours=1)).strftime('%H:%M')} - {change.end.__add__(datetime.timedelta(hours=1)).strftime('%H:%M')}\n"
                desc += f"{change.location}\n"
                desc += f"{change.description.strip()[:-30]}\n"
            embed = discord.Embed(
                title="Ton EDT a changé !",
                description="Voici les changements qui ont eu lieu :\n" + desc,
            )
            pprint.pprint(embed.to_dict())
            await c.send(embed=embed)
            #TODO: When a course is deleted, it is not 'detected'


def init_newsletter():
    with open('newsletter.txt', 'r') as f:
        d = {}
        for line in f.readlines():
            id, discordID = line.strip().split(sep=';')
            d[(int(id), int(discordID))] = getEDT(id=int(id), dateS=datetime.date(2022, 9, 5), dateF=datetime.date(2023, 7, 24))
        students_edt.update(d)

def save_newsletter():
    with open('newsletter.txt', 'w') as f:
        for student in students_edt.keys():
            f.write(f"{student[0]};{student[1]}\n")

@bot.command(name='AddNewsletter')
async def add_student_to_newsletter(ctx, id: int):
    students_edt[(id, ctx.author.id)] = getEDT(id=id, dateS=datetime.date(2022, 9, 5), dateF=datetime.date(2023, 7, 24))
    await ctx.send('Added to newsletter')

@bot.command(name='RemoveNewsletter')
async def remove_student_from_newsletter(ctx, id: int):
    del students_edt[(id, ctx.author.id)]
    await ctx.send('Removed from newsletter')

@bot.command(name='nextClass')
async def next_class(ctx, id: int):
    if (id, ctx.author.id) not in students_edt:
        calendar = getEDT(id=id, dateS=datetime.date.today(), dateF=datetime.date.today().__add__(datetime.timedelta(days=7)))
        e = nextClass(calendar)
        if e is None:
            await ctx.send('No class today')
        else:
            await ctx.send(f"Next class is {e.name} at {e.begin.__add__(datetime.timedelta(hours=1)).strftime('%H:%M')}\n{e.location}\n{e.description.strip()[:-30]}")

    else:
        e = nextClass(students_edt[(id, ctx.author.id)])
        if e is None:
            await ctx.send('No class today')
        else:
            await ctx.send(f"Next class is {e.name} at {e.begin.__add__(datetime.timedelta(hours=1)).strftime('%H:%M')}\n{e.location}\n{e.description.strip()[:-30]}")


@bot.command(name='Occupied')
async def occupied(ctx):
    l = findCurrentlyOccupiedRooms()
    if len(l) == 0:
        await ctx.send('No room is occupied')
    else:
        await ctx.send(f"Currently occupied rooms are : {', '.join(l)}")



@bot.event
async def on_ready():
    print('Gentlemen')
    await bot.change_presence(activity=discord.Game(name='with your soul'))
    init_newsletter()
    #grades.start()
    edt_newsletter.start()
    print('Mentlegen')

@bot.command(name='stop')
@commands.is_owner()
async def stop(ctx):
    edt_newsletter.stop()
    #await grades.stop()
    save_newsletter()
    await bot.close()
    exit(0)

if __name__ == '__main__':
    bot.run(TOKEN)