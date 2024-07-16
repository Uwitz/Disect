import os
import traceback

from typing import List

from discord import Interaction, Object
from discord.app_commands import Choice, Group, command, describe
from discord.ext.commands import Bot, Cog

class Admin(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot

	async def unloaded_extensions(
		self,
		interaction: Interaction,
		current: str
	) -> List[Choice[str]]:
		return [
			Choice(
				name = extension,
				value = extension
			)
			for extension in [
				extension[:-3]
				for extension in os.listdir("./cogs") if extension.endswith(".py")
			] if (current.lower() in extension.lower()) and (extension not in self.bot.loaded_extensions)
		]

	async def loaded_extensions(
		self,
		interaction: Interaction,
		current: str
	) -> List[Choice[str]]:
		return [
			Choice(
				name = extension,
				value = extension
			)
			for extension in [
				extension[:-3]
				for extension in os.listdir("./cogs") if extension.endswith(".py")
			] if (current.lower() in extension.lower()) and (extension in self.bot.loaded_extensions)
		]

	cog = Group(name="cog")

	@cog.command(name = "load", description = "Load a cog.")
	@cog.autocomplete(extension = unloaded_extensions)
	async def load(self, interaction: Interaction, extension: str):
		try:
			await self.bot.load_extension(f"cogs.{extension}")
			await interaction.response.send_message(
				f"{os.getenv('EMOJI_SUCCESS')} Loaded `cogs.{extension}` extension"
			)
		except Exception as error:
			await interaction.response.send_message(
				f"{os.getenv("EMOJI_FAIL")} Unable to load `cogs.{extension}`\n```python\n{error}\n```",
				ephemeral = True
			)

	@cog.command(name = "unload", description = "Unload a cog.")
	@cog.describe(name = "extension", description = "Extension file to unload.")
	@cog.autocomplete(extensions = loaded_extensions)
	async def unload(self, interaction: Interaction, extension):
		try:
			await self.bot.unload_extension(f"cogs.{extension}")
			await interaction.response.send_message(
				f"{os.getenv('EMOJI_SUCCESS')} Unloaded `cogs.{extension}` extension"
			)
		except Exception as error:
			await interaction.response.send_message(
				f"{os.getenv("EMOJI_FAIL")} Unable to unload `cogs.{extension}`\n```python\n{error}\n```",
				ephemeral = True
			)

	@cog.command(name = "reload", description = "Reload a cog.")
	@cog.describe(name = "extension", description = "Extension file to unload.")
	@cog.autocomplete(extensions = loaded_extensions)
	async def unload(self, interaction: Interaction, extension):
		try:
			await self.bot.reload_extension(f"cogs.{extension}")
			await interaction.response.send_message(
				f"{os.getenv('EMOJI_SUCCESS')} Reloaded `cogs.{extension}` extension"
			)
		except Exception as error:
			await interaction.response.send_message(
				f"{os.getenv("EMOJI_FAIL")} Unable to reload `cogs.{extension}`\n```python\n{error}\n```",
				ephemeral = True
			)

async def setup(bot: Bot):
	await bot.add_cog(Admin(bot), guild = Object(os.getenv("GUILD")))