import discord
from discord.ext import commands 
import responses
from dotenv import load_dotenv
import os

load_dotenv()  

async def send_message(ctx, *, message):
    try:
        response = responses.handle_response(message)
        await ctx.author.send(response) if is_private else await ctx.send(response)

    except Exception as e:
        print(e)


def run_discord_bot():
    
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    intents=discord.Intents.all()
    intents.message_content = True
    client = commands.Bot(command_prefix = '>', intents = intents)

    @client.event
    async def on_ready():
        print(f'{client.user.name} is running')

    @client.command(aliases=["hi", "hey"])
    async def hello(ctx):
        await ctx.send(f"Hey there, {ctx.author.mention}!")

    @client.command(aliases=["Roll", "roll"])
    async def sendembed(ctx):
            embed = discord.Embed(title="Title of embed", description="Description", color=discord.Color.blue())
            embed.set_thumbnail(url="https://i.imgur.com/u1JDiwv.jpeg")
            embed.add_field(name="Name of Field", value="Value of Field", inline=False)
            guild_icon_url = str(ctx.guild.icon.url)         
            embed.set_image(url=guild_icon_url)
            embed.set_footer(text="Footer Text", icon_url=ctx.author.avatar)
            
            await ctx.send(embed=embed)

  
        
   
    # @client.event
    # async def on_message(message):
    #     if message.author.bot:
    #         return

    #     print(f'{str(message.author)} said: "{str(message.content)}" in ({str(message.channel)})')
    #     if message.content.startswith('$'):
    #         try:
    #             response = responses.handle_response(message.content[1:])
    #             await message.channel.send(response)
    #         except Exception as e:
    #             print(e)



    client.run(TOKEN)