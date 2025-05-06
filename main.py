from xml.sax import handler
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests

load_dotenv()
token = os.environ.get('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.webhooks = True

bot = commands.Bot(command_prefix='!', intents=intents)

admin_role = "admin"
vip_role = "⛥ Saints ⛥"
elite_role = "⛥ Elite Saints ⛥"

from keep_alive import keep_alive
keep_alive()

def username_to_member(guild: discord.Guild, name:str):
    "Returns None if name not found in guild"
    for member in guild.members:
        if member.name == name:
            return member
    return None

@bot.event
async def on_ready():
   print(f'Logged in as {bot.user.name} - {bot.user.id}')
   print('------')
   await bot.change_presence(status=discord.Status.online, activity=discord.Game(name='Elite Saints In World'))#name='Elite Saints VIP In World'))

@bot.command()
@commands.has_role(admin_role)
async def assign(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name=elite_role)
    if role:
        await member.add_roles(role)
        await ctx.send(f'Role {role.name} has been assigned to {member.mention}')
    else:
        await ctx.send(f'Role {elite_role} not found in this server.')

@bot.command()
@commands.has_role(admin_role)
async def remove(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name=elite_role)
    if role:
        await member.remove_roles(role)
        await ctx.send(f'Role {role.name} has been removed from {member.mention}')
    else:
        await ctx.send(f'Role {elite_role} not found in this server.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    #if message.channel.name != 'subscription-events':
    #    return
    # Check if the message is from a webhook
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
            if len(parts) == 7:
                username = parts[2]
                baseRole = discord.utils.get(message.guild.roles, name=vip_role)
                eliteRole = discord.utils.get(message.guild.roles, name=elite_role)
                if baseRole and eliteRole:
                    foundMember = username_to_member(message.guild, username)
                    if foundMember:
                        await foundMember.add_roles(baseRole)
                        await foundMember.add_roles(eliteRole)
                        await message.channel.send(f'{foundMember.mention} Now has the {baseRole.name} and {eliteRole.name} role. [Profile Link]({parts[1]})```Paid at {parts[3]}\nExpires at {parts[4]}```')
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

bot.run(token, log_handler=handler, log_level=logging.DEBUG)