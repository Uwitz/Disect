import os

from typing import List

from discord import Interaction, Object
from discord.app_commands import Choice, Group, autocomplete
from discord.ext.commands import Bot, Cog

class Admin(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot

	async def unloaded_extension_list(
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
			] if (current.lower() in extension.lower()) and (extension not in self.bot.loaded_extension_list)
		]

	async def loaded_extension_list(
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
			] if (current.lower() in extension.lower()) and (extension in self.bot.loaded_extension_list)
		]

	cog = Group(name="cog", description = "Group of commands to manage cogs.")

	@cog.command(name = "load", description = "Load a cog.")
	@autocomplete(extension = unloaded_extension_list)
	async def load(self, interaction: Interaction, extension: str):
		try:
			await self.bot.load_extension(f"cogs.{extension}")
			await interaction.response.send_message(
				f"{os.getenv('EMOJI_SUCCESS')} Loaded `cogs.{extension}` extension"
			)
		except Exception as error:
			await interaction.response.send_message(
				f"{os.getenv('EMOJI_FAIL')} Unable to load `cogs.{extension}`\n```python\n{error}\n```",
				ephemeral = True
			)

	@cog.command(name = "unload", description = "Unload a cog.")
	@autocomplete(extension = loaded_extension_list)
	async def unload(self, interaction: Interaction, extension: str):
		if extension == "admin":
			return await interaction.response.send_message(f"{os.getenv('EMOJI_FAIL')} Unloading `cogs.{extension}` is disallowed")
		try:
			await self.bot.unload_extension(f"cogs.{extension}")
			await interaction.response.send_message(
				f"{os.getenv('EMOJI_SUCCESS')} Unloaded `cogs.{extension}` extension"
			)
		except Exception as error:
			await interaction.response.send_message(
				f"{os.getenv('EMOJI_FAIL')} Unable to unload `cogs.{extension}`\n```python\n{error}\n```",
				ephemeral = True
			)

	@cog.command(name = "reload", description = "Reload a cog.")
	@autocomplete(extension = loaded_extension_list)
	async def reload(self, interaction: Interaction, extension: str):
		try:
			await self.bot.reload_extension(f"cogs.{extension}")
			await interaction.response.send_message(
				f"{os.getenv('EMOJI_SUCCESS')} Reloaded `cogs.{extension}` extension"
			)
		except Exception as error:
			await interaction.response.send_message(
				f"{os.getenv('EMOJI_FAIL')} Unable to reload `cogs.{extension}`\n```python\n{error}\n```",
				ephemeral = True
			)

async def setup(bot: Bot):
	await bot.add_cog(Admin(bot), guild = Object(os.getenv("GUILD")))