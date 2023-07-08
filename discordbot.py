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


@bot.tree.command(name="test", description="スラッシュコマンドが機能しているかのテスト用コマンド")
async def test(interaction: discord.Interaction):
    print("test")
    await interaction.response.send_message("test")


# イベントを検知
@bot.event
# botの起動が完了したとき
async def on_ready():
    print("Hello!")  # コマンドラインにHello!と出力


# メッセージ編集時に発動(編集前(before)と後(after)のメッセージを送信)
@bot.event
async def on_message_edit(before, after):
    txt = f"{before.author} がメッセージを編集しました！\nbefore:```{before.content}```\nafter:```{after.content}```"
    await after.add_reaction()
    await before.channel.send(txt)


# メッセージ削除時に発動(削除されたメッセージを送信)
@bot.event
async def on_message_delete(message):
    txt = f"{message.channel}:{message.author} がメッセージを削除しました！\n```{message.content}```"
    await message.author.send(txt)
    await message.channel.send(txt)


@bot.event
async def on_typing(channel, user, when):
    txt = f"{user} がメッセージを入力しています！"
    await channel.send(txt)


async def main():
    # コグのフォルダ
    cogfolder = "cogs."
    # そして使用するコグの列挙(拡張子無しのファイル名)
    cogs = ["sample_cog"]

    for c in cogs:
        await bot.load_extension(cogfolder + c)

    # start the client
    async with bot:
        await bot.start(APITOKEN)

asyncio.run(main())
