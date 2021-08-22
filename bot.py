import os
import random
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$')


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    print(f'{bot.user} Joined the following Guilds : ')
    for guild in bot.guilds:
        print(
            f'<*> {guild.name} with id {guild.id} with {len(guild.members)} members')
        members = '\n - '.join([member.name for member in guild.members])
        print(f'< > Guild Members:\n     - {members}')


@bot.command(name='add-note')
async def add_note(ctx, *note: str):
    user_id = ctx.message.author.id
    file = open(f'./save_file/{user_id}', 'a')
    file.writelines('\n' + ' '.join(note))
    file.close()
    await ctx.send("Note Saved !")


@bot.command(name='view-note')
async def view_note(ctx):
    user_id = ctx.message.author.id
    file = open(f'./save_file/{user_id}', 'r')
    note = file.readlines()
    note = ''.join(note)
    await ctx.send(f"Your Note is : \n{note}")


@bot.command(name='hello')
async def hello(ctx):
    await ctx.send("Hello Too !!")


@bot.command(name='roll-dice', help="Simulates rolling dice, you can put custom number of dice, and number of sides")
async def roll(ctx, number_of_dice: int = 1, number_of_sides: int = 6):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))


@bot.command(name='create-channel', help="Creating new Channel")
@commands.has_role('admin')
async def create_channel(ctx, channel_name: str):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating new channel named {channel_name}')
        await guild.create_text_channel(channel_name)
    await ctx.send(f'Channel {channel_name} created !')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have permission')

bot.run(TOKEN)
