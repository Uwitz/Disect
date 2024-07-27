import os
import traceback

from dotenv import find_dotenv, load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any, Coroutine

from discord import Intents, Object
from discord.ext.commands import Bot

from encryption import Encryption

class System(Bot):
	def __init__(self):
		self.loaded_extension_list = []
		self.unloaded_extension_list = []
		intents = Intents.all()
		super().__init__(intents = intents, command_prefix = "/")

	async def start(self, *args, **kwargs):
		self.core_guild = int(os.getenv("GUILD"))
		await super().start(*args, **kwargs)

	async def sync_commands(self):
		await self.tree.sync(guild = Object(id = self.core_guild))
		await self.tree.sync()

	async def setup_hook(self) -> Coroutine[Any, Any, None]:
		self.encryption = Encryption()
		try:
			self.encryption.load_credentials()
		except FileNotFoundError:
			self.encryption.generate_credentials()

		if os.getenv("MONGO_TLS") == "True":
			self.database = AsyncIOMotorClient(
				os.getenv("MONGO"),
				tls = True,
				tlsCertificateKeyFile = "mongo_cert.pem"
			)["disect"]
			self.chatsync_db = AsyncIOMotorClient(
				os.getenv("MONGO"),
				tls = True,
				tlsCertificateKeyFile = "mongo_cert.pem"
			)["channelsync"]
		else:
			self.database = AsyncIOMotorClient(os.getenv("MONGO"))["disect"]
			self.chatsync_db = AsyncIOMotorClient(os.getenv("MONGO"))["channelsync"]

		for file in os.listdir("./cogs"):
			if file.endswith(".py"):
				try:
					await self.load_extension(f"cogs.{file[:-3]}")
					self.loaded_extension_list.append(file[:-3])
					print(f"Loaded \"{file[:-3]}\" extension")
				except Exception as error:
					self.unloaded_extension_list.append(file[:-3])
					traceback.print_exc(error)

		self.loop.create_task(self.sync_commands())

if __name__ == "__main__":
	load_dotenv(find_dotenv())
	bot = System()
	bot.run(os.getenv("TOKEN"))