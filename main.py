#from xml.sax import handler
import discord
from discord.ext import commands
import logging
#from dotenv import load_dotenv
import os
import requests

from flask import Flask, render_template
from threading import Thread

#load_dotenv()
token = os.environ.get('DISCORD_TOKEN')

#handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
#intents.webhooks = True

bot = commands.Bot(command_prefix='!', intents=intents)#discord.Client(intents=intents)#

admin_role = "admin"
vip_role = "⛥ Saints ⛥"
elite_role = "⛥ Elite Saints ⛥"

bot.run(token)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name != 'subscription-events':
        return
    #Check if the message is from a webhook
    if message.webhook_id:
        # Parse the content of the webhook message
        if message.content.startswith('slUserRegistration'):
            #print('start reg')
            parts = message.content.split('::')
            if len(parts) == 4:
                username = parts[2]
                #print('searching member')
                foundMember = username_to_member(message.guild, username)
                #print('username found')
                if foundMember:
                    await message.delete()  # Delete the webhook message after processing
                    #print('deleted')
                    requests.post(parts[3], json={'responseType' : 'registrationResult', 'success' : 'true', 'userId' : parts[1], 'discordName' : username})
                    #print('posted')
                else:
                    await message.delete()  # Delete the webhook message after processing
                    requests.post(parts[3], json={'responseType' : 'registrationResult', 'success' : 'false', 'userId' : parts[1], 'discordName' : username})
        elif message.content.startswith('slRoleAssign'):
            parts = message.content.split('::')
            if len(parts) == 8:
                username = parts[2]
                baseRole = discord.utils.get(message.guild.roles, name=vip_role)
                eliteRole = discord.utils.get(message.guild.roles, name=elite_role)
                if baseRole and eliteRole:
                    foundMember = username_to_member(message.guild, username)
                    if foundMember:
                        await foundMember.add_roles(baseRole)
                        await foundMember.add_roles(eliteRole)
                        await message.channel.send(f'{foundMember.mention} purchased {parts[7]} days.\nThey now have the {baseRole.name} and {eliteRole.name} role. [Profile Link]({parts[1]})```Paid at {parts[3]}\nExpires at {parts[4]}```')
                            #print('Gave role')
                        await message.delete()  # Delete the webhook message after processing
                        requests.post(parts[5], json={'responseType' : 'roleResult', 'success' : 'true', 'userId' : parts[6]})
                            #print('second posted')
                    else:
                        await message.channel.send(f'Username "{username}" not found in this server.\nPlease inform the purchaser:[Profile Link]({parts[1]})')
                        requests.post(parts[5], json={'responseType' : 'roleResult', 'success' : 'false'})
                else:
                    await message.channel.send(f'Role {elite_role} or {vip_role} not found in this server.')
        elif message.content.startswith('slRoleRemove'):
            parts = message.content.split('::')
            if len(parts) == 6:
                username = parts[2]
                role = discord.utils.get(message.guild.roles, name=elite_role)
                if role:
                    foundMember = username_to_member(message.guild, username)
                    if foundMember:
                        await foundMember.remove_roles(role)
                        await message.channel.send(f'{foundMember.mention}\'s membership from `{parts[3]}` expired at `{parts[4]}`. [Profile Link]({parts[1]})')
                        await message.delete()  # Delete the webhook message after processing
                        #requests.post(parts[5], json={'bean' : 'goodbye'})
                    else:
                        await message.channel.send(f'Removing {elite_role} member with username "{username}" not found in this server.')
                else:
                    await message.channel.send(f'Role {elite_role} not found in this server.')
    
    await bot.process_commands(message)

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=port)
