import os
import random
import logging
from discord.enums import ChannelType
from dotenv import load_dotenv
import discord
from discord.ext import commands
import json
import requests
from Huggingface_App import HuggingfaceApp


# Loading environment variable from the textfile and save in in a variable
load_dotenv()
HF_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
TOKEN = os.getenv('DISCORD_TOKEN')

# Model from hugging face that we want to use
HF_API_URL = 'https://api-inference.huggingface.co/models/microsoft/'
MODEL_NAME = 'DialoGPT-large'

# Creating necessary object :
# bot object from discord.py Bot class
# initialize huggingface chatbot agent
bot = commands.Bot(command_prefix='$')
hf_chat_bot_agent = HuggingfaceApp(HF_API_URL, MODEL_NAME, HF_TOKEN)


@bot.event
async def on_message(message):
    """
    this function is called whenever the bot sees a message in a channel
    """
    # ignore the message if it comes from the bot itself
    if message.author.id == bot.user.id:
        return

    if message.channel != 'Adv Bot':
        return

    # form query payload with the content of the message
    payload = {'inputs': {'text': message.content}}

    # while the bot is waiting on a response from the model
    # set the its status as typing for user-friendliness
    async with message.channel.typing():
        response = hf_chat_bot_agent.query(payload)
    bot_response = response.get('generated_text', None)

    # we may get ill-formed response if the model hasn't fully loaded
    # or has timed out
    if not bot_response:
        if 'error' in response:
            bot_response = '`Error: {}`'.format(response['error'])
        else:
            bot_response = 'Hmm... something is not right.'

    # send the model's response to the Discord channel
    await message.channel.send(bot_response)


@bot.event
async def on_ready():
    """functino that is called when discord bot done initializing when first running"""
    print('Connected to Discord!')
    print(f'Guild list : {[guild.name for guild in bot.guilds]}')


@bot.command(name='add-note', help='to save a note')
async def add_note(ctx, *note: str):
    """Function called when user have command add-note
    It is for creating note
    """
    user_id = ctx.message.author.id
    file = open(f'./save_file/{user_id}', 'a')
    file.writelines('\n' + ' '.join(note))
    file.close()
    await ctx.send("Note Saved !")


@bot.command(name='view-note', help='to view your saved note')
async def view_note(ctx):
    """To display note from specific user"""
    user_id = ctx.message.author.id
    file = open(f'./save_file/{user_id}', 'r')
    note = file.readlines()
    if not note:
        await ctx.send("You dont have saved notes !")
        return
    note = "- " + '- '.join(note)
    await ctx.send(f"Your Note is : \n{note}")


@bot.command(name='hello', help='To say hello')
async def hello(ctx):
    """It returns back word hello!"""
    await ctx.send("Hello Too !!")


@bot.command(name='roll-dice', help="Simulates rolling dice, you can put custom number of dice, and number of sides")
async def roll(ctx, number_of_dice: int = 1, number_of_sides: int = 6):
    """function for simulating rolling dice"""
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))


@bot.command(name='create-channel', help="If you need help to create a new channel")
@commands.has_role('admin')
async def create_channel(ctx, channel_name: str):
    """For creating specific text channel"""
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
