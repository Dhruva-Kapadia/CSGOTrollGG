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
    client = commands.Bot(command_prefix = '$', intents = intents)

    @client.event
    async def on_ready():
        print(f'{client.user.name} is running')

    @client.event
    async def on_message(message):
        if message.author.bot:
            return

        print(f'{str(message.author)} said: "{str(message.content)}" in ({str(message.channel)})')
        if message.content.startswith('$'):
            try:
                response = responses.handle_response(message.content[1:])
                await message.channel.send(response)
            except Exception as e:
                print(e)



    client.run(TOKEN)