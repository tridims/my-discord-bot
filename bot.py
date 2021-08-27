import os
import random
import logging
from discord.enums import ChannelType
from dotenv import load_dotenv
import discord
from discord.ext import commands
import json
import requests
from ChatReply import ChattingBot


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
HF_API_URL = 'https://api-inference.huggingface.co/models/microsoft/'
MODEL_NAME = 'DialoGPT-large'
HF_TOKEN = os.getenv('HUGGINGFACE_TOKEN')


bot = commands.Bot(command_prefix='$')
hf_chat_bot_agent = ChattingBot(HF_API_URL, MODEL_NAME, HF_TOKEN)


@bot.event
async def on_message(message):
    """
    this function is called whenever the bot sees a message in a channel
    """
    # ignore the message if it comes from the bot itself
    if message.author.id == bot.user.id:
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
    print('Connected to Discord!')
    print(f'Guild list : {[guild.name for guild in bot.guilds]}')


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
