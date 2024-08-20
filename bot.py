import discord
from discord.ext import commands 
import responses

async def send_message(ctx, *, message):
    try:
        response = responses.handle_response(message)
        await ctx.author.send(response) if is_private else await ctx.send(response)

    except Exception as e:
        print(e)


def run_discord_bot():
    
    TOKEN = 'MTE2MTAwMjM4ODE1NzY0NDk1MA.G88ILP.TSQ8mAY0wwJBHKhuYCCwEEvBmv8h_XEuOFNW8Q'
    intents=discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix = '>', intents = intents)

    @client.event
    async def on_ready():
        print(f'{client.user.name} is running')

    @client.command(aliases=["hi", "hey"])
    async def hello(ctx):
        await ctx.send(f"Hey there, {ctx.author.mention}!")

    @client.command(name="Roll")
    async def sendembed(ctx):
        embeded_msg.set_author(text="Author Text", icon_url=ctx.author.avatar)
        embeded_msg = discord.Embed(title = "Title of embed", description="Description", color=discord.color.green())
        embeded_msg.set_thumbnail(url="https://i.imgur.com/u1JDiwv.jpeg")
        embeded_msg.add_field(name = "Name of Field", Value="Value of Field", inline=True)
        embeded_msg.set_image(url=ctx.guild.icon)
        embeded_msg.set_footer(text="Footer Text", icon_url=ctx.author.avatar)
  
        
   
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