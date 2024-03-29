import os
import traceback

from dotenv import find_dotenv, load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any, Coroutine

from discord import Intents, Object
from discord.ext.commands import Bot

class System(Bot):
	def __init__(self):
		intents = Intents.all()
		super().__init__(intents = intents, command_prefix = "/")

	async def start(self, *args, **kwargs):
		if os.getenv("MONGO_TLS") == "True":
			self.database = AsyncIOMotorClient(
				os.getenv("MONGO"),
				tls = True,
				tlsCertificateKeyFile = "mongo_cert.pem"
			)
		else:
			self.database = AsyncIOMotorClient(os.getenv("MONGO"))
		self.core_guild = int(os.getenv("GUILD"))
		await super().start(*args, **kwargs)

	async def sync_commands(self):
		await self.tree.sync(guild = Object(id = self.core_guild))
		await self.tree.sync()

	async def setup_hook(self) -> Coroutine[Any, Any, None]:
		for file in os.listdir("./cogs"):
			if file.endswith(".py"):
				try:
					await self.load_extension(f"cogs.{file[:-3]}")
					print(f"Loaded \"{file[:-3].capitalize()}\" extension")
				except Exception as error:
					traceback.print_exc(error)

		self.loop.create_task(self.sync_commands())

if __name__ == "__main__":
	load_dotenv(find_dotenv())
	bot = System()
	bot.run(os.getenv("TOKEN"))