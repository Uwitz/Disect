import os

from typing import List

from discord import Embed, Interaction, Object
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
			self.bot.loaded_extension_list.remove(extension)
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

	@cog.command(name = "health", description = "Check the bot's developer information.")
	async def health(self, interaction: Interaction):
		unloaded_extensions = [
			extension
			for extension in [
				extension[:-3]
				for extension in os.listdir("./cogs") if extension.endswith(".py")
			] if extension not in self.bot.loaded_extension_list
		]
		unloaded_extensions = ["null"] if len(unloaded_extensions) == 0 else unloaded_extensions
		ping = round(self.bot.latency * 1000)
		efficiency_description = "peak" if ping <= 50 and len(unloaded_extensions) == 0 else "degraded"
		embed = Embed(
			description = f"Discord Bot online and functional with {efficiency_description} performance.",
			colour = 0x2B2D31
		)

		if ping <= 50:
			embed.add_field(
				name = "> Ping",
				value = f"{os.getenv('EMOJI_GOODPING')} {ping}ms",
				inline = False
			)
		elif ping <= 125:
			embed.add_field(
				name = "> Ping",
				value = f"{os.getenv('EMOJI_MODERATEPING')} {ping}ms",
				inline = False
			)
		else:
			embed.add_field(
				name = "> Ping",
				value = f"{os.getenv('EMOJI_BADPING')} {ping}ms",
				inline = False
			)

		embed.add_field(
			name = "> Loaded",
			value = f"```diff\n+ {'\n+ '.join(self.bot.loaded_extension_list)}\n```",
			inline = True
		).add_field(
			name = "> Unloaded",
			value = f"```diff\n- {'\n- '.join(unloaded_extensions)}\n```",
			inline = True
		)

		if len(unloaded_extensions) > 0 or ping >= 125:
			embed.set_author(
				name = "Health Status",
				icon_url = "https://cdn.uwitz.org/r/degraded-health.png"
			)

		elif self.bot.internal_error_occured:
			embed.set_author(
				name = "Health Status",
				icon_url = "https://cdn.uwitz.org/r/critical-health.png"
			)

		else:
			embed.set_author(
				name = "Health Status",
				icon_url = "https://cdn.uwitz.org/r/good-health.png"
			)

		await interaction.response.send_message(embed = embed, ephemeral = True)

async def setup(bot: Bot):
	await bot.add_cog(Admin(bot), guild = Object(os.getenv("GUILD")))