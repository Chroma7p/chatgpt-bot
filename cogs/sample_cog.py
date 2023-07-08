from discord.ext import commands
from discord import app_commands
import discord

# samplecogクラス


class SampleCog(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    # Cogが読み込まれた時に発動
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.tree.sync()
        print('SampleCog on ready!')

    # コマンドの記述
    @app_commands.command(name="chkcog", description="SampleCogが機能しているかのテスト用コマンド")
    async def chkcog(self, interaction: discord.Interaction):
        await interaction.response.send_message("SampleCog is working!")


# Cogとして使うのに必要なsetup関数
def setup(bot):
    return bot.add_cog(SampleCog(bot))
