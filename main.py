#from xml.sax import handler
import discord
from discord.ext import commands
import logging
#from dotenv import load_dotenv
import os
import requests

#from flask import Flask, render_template
#from threading import Thread

#load_dotenv()
token = os.environ.get('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
#intents.webhooks = True

bot = commands.Bot(command_prefix='!', intents=intents)#discord.Client(intents=intents)#

admin_role = "admin"
vip_role = "⛥ Saints ⛥"
elite_role = "⛥ Elite Saints ⛥"

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
