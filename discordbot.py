# discord.pyの大事な部分をimport
from discord.ext import commands
import discord
import os
import asyncio
from dotenv import load_dotenv

load_dotenv(".env")

# デプロイ先の環境変数にトークンをおいてね
APITOKEN = os.environ["DISCORD_BOT_TOKEN"]
# botのオブジェクトを作成(コマンドのトリガーを!に)
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())


# イベントを検知
@bot.event
# botの起動が完了したとき
async def on_ready():
    print("Logged in as")
    print(bot.user.name)

async def main():
    # コグのフォルダ
    cogfolder = "cogs."
    # そして使用するコグの列挙(拡張子無しのファイル名)
    cogs = ["main_cog"]

    for c in cogs:
        await bot.load_extension(cogfolder + c)

    # start the client
    async with bot:
        await bot.start(APITOKEN)

asyncio.run(main())
