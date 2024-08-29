from discord.ext.commands import Bot, Cog

class ErrorHandler(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener("on_error")
    async def error_event(self, exception):
        print(f"ERROR:\n{exception}")
        self.bot.internal_error_occured = True

async def setup(bot: Bot):
    await bot.add_cog(ErrorHandler(bot))