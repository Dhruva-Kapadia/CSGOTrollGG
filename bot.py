import asyncio
from sys import argv
import discord
from discord.ext import commands 
from cogs.claim_cog import Claims
from cogs.guild_joined_cog import GuildJoin
from cogs.hello_cog import Hello
from cogs.help_cog import HelpCommand
from cogs.roll_cog import Roll
from cogs.timer_cog import Timers
from dotenv import load_dotenv
import os
from cogs.inventory_cog import Inventory
from cogs.tradeup import Tradeup
from db_connect import get_db_connection

load_dotenv()

def run_discord_bot():
    
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    intents = discord.Intents.all()
    intents.message_content = True
    client = commands.Bot(command_prefix='>', intents=intents)

    async def reset_can_claim():
        while True:
            try:
                await asyncio.sleep(1)
                
                connection = get_db_connection()
                
                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute("UPDATE server_user SET can_claim = 1 WHERE can_claim = 0")
                    connection.commit()
                else:
                    print("Failed to connect to database")
            except Exception as e:
                print(f"An error occurred: {str(e)}")
            finally:
                if connection is not None and connection.is_connected():
                    cursor.close()
                    connection.close()

    async def main():
        await client.add_cog(GuildJoin(client))
        await client.add_cog(Hello(client))
        await client.add_cog(HelpCommand(client))
        await client.add_cog(Inventory(client))
        await client.add_cog(Timers(client))
        await client.add_cog(Claims(client))
        await client.add_cog(Roll(client))
        await client.add_cog(Tradeup(client))

        @client.event
        async def on_ready():
            await client.change_presence(activity=discord.Game(name='>h'))
            print(f'{client.user.name} is running')
            client.loop.create_task(reset_can_claim())

        await client.start(TOKEN)

    asyncio.run(main())

if __name__ == "__main__":
    run_discord_bot()
