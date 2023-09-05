from discord.ext import commands
from discord import app_commands
import discord
import os
import dotenv
from chatgpt import Chat,Role

dotenv.load_dotenv(".env")

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

CHANNEL_LIST = [int(i) for i in os.environ["CHANNEL_LIST"].split(",")]

chats = {channel_id : Chat(API_KEY=OPENAI_API_KEY) for channel_id in CHANNEL_LIST}

# samplecogクラス
class MainCog(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    # Cogが読み込まれた時に発動
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()
        print('MainCog on ready!')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        channel = message.channel
        if channel.id in CHANNEL_LIST:
            try:
                msg= await message.reply(content="please wait...")
                reply=""
                next=40
                async with message.channel.typing():
                    response = chats[channel.id].stream_send(message.content)
                    chats[channel.id].add("",role=Role.assistant)
                    response_idx = len(chats[channel.id].history)-1
                    for chunk in response:
                        if "content" in chunk["choices"][0]["delta"]:
                            reply += chunk["choices"][0]["delta"]["content"]
                        if chunk["choices"][0]["finish_reason"] == "stop":
                            break

                        if len(reply) > next:
                            await msg.edit(content=reply)
                            chats[channel.id].history[response_idx].content = reply
                            next += 40
                    await msg.edit(content=reply)
                    chats[channel.id].history[response_idx].content = reply

            except Exception as e:
                await channel.send(f"エラーが発生しました\n```{e}```")
                return await self.bot.process_commands(message)
        
        return await self.bot.process_commands(message)

    # コマンドの記述
    @app_commands.command(name="model", description="ChatGPTのモデルを変更します")
    @app_commands.describe(model_name="ChatGPTのモデル")
    @app_commands.choices(
        model_name= [app_commands.Choice(name="gpt-3.5-turbo", value="gpt-3.5-turbo-0613"),
         app_commands.Choice(name="gpt-3.5-turbo-16k", value="gpt-3.5-turbo-0613"),
         app_commands.Choice(name="gpt-4", value="gpt-4-0613"),
         app_commands.Choice(name="gpt-4-32k", value="gpt-4-32k-0613"),
         ]
    )
    async def model(self, interaction:discord.Interaction, model_name: app_commands.Choice[str]):
        channel = interaction.channel
        if channel.id in CHANNEL_LIST:
            try:
                chats[channel.id].set_model(model_name.value)
            except Exception as e:
                await interaction.response.send_message(f"モデルの変更に失敗しました\n```{e}```")

            await interaction.response.send_message(f"モデルを`{model_name.value}`に変更しました")
        else:
            await interaction.response.send_message(f"このチャンネルではこのコマンドは使えません")
            
    @app_commands.command(name="reset", description="チャットをリセットします")
    async def reset(self, interaction:discord.Interaction):
        channel = interaction.channel
        if channel.id in CHANNEL_LIST:
            try:
                chats[channel.id].reset()
            except Exception as e:
                await interaction.response.send_message(f"リセットに失敗しました\n```{e}```")

            await interaction.response.send_message(f"リセットしました")
        else:
            await interaction.response.send_message(f"このチャンネルではこのコマンドは使えません")


# Cogとして使うのに必要なsetup関数
def setup(bot):
    return bot.add_cog(MainCog(bot))


