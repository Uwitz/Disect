import asyncio
import os
import json
import traceback

from dotenv import find_dotenv, load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any, Coroutine

from discord import Intents, Object
from discord.ext.commands import Bot

class Client(Bot):
	def __init__(self):
		with open("metadata.json") as metadata_file:
			self.metadata = json.load(metadata_file)
		self.build = self.metadata.get("build")
		self.loaded_extension_list = []
		self.unloaded_extension_list = []
		self.internal_error_occured = False
		intents = Intents.all()
		super().__init__(intents = intents, command_prefix = "/")

	async def start(self, *args, **kwargs):
		self.core_guild = int(self.bot.metadata.get("guild_id"))
		await super().start(*args, **kwargs)

	async def sync_commands(self):
		await self.tree.sync(guild = Object(id = self.core_guild))
		await self.tree.sync()

	async def setup_hook(self) -> Coroutine[Any, Any, None]:
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
		
		for file in os.listdir("./cogs"):
			if file.endswith(".py"):
				try:
					await self.load_extension(f"cogs.{file[:-3]}")
					self.loaded_extension_list.append(file[:-3])
					print(f"Loaded \"{file[:-3]}\" extension")
				except Exception as error:
					self.unloaded_extension_list.append(file[:-3])
					traceback.print_exc(error)
					continue

		self.loop.create_task(self.sync_commands())

async def main():
	load_dotenv(find_dotenv())
	bot = Client()
	async with bot:
		await bot.start(os.getenv("TOKEN"))

if __name__ == "__main__":
	asyncio.run(main())
