import os

from dotenv import find_dotenv, load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from discord import Intents
from discord.ext.commands import Bot

class System(Bot):
	def __init__(self):
		indents = Indents.all()
		super().__init__(indents = indents, command_prefix = "/")

	async def start(self, *args, **kwargs):
		load_dotenv(find_dotenv())
		self.database = AsyncIOMotorClient(os.getenv("MONGO"))
		self.core_guild = int(os.getenv("GUILD"))
		await super().start(*args, **kwargs)

	async def sync_commands(self):
		await self.tree.sync(guild = Object(id = self.guild_id))
		await self.tree.sync()

	async def setup_hook(self) -> Coroutine[Any, Any, None]:
		for file in os.listdir("./cogs"):
			if file.endswith(".py"):
				await self.load_extension(f"cogs.{file[:-3]}")

		self.loop.create_task(self.sync_commands())

if __name__ == "__main__":
	bot.run(os.getenv("TOKEN"))