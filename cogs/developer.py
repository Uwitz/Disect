import os
import traceback

from typing import List

from discord import Embed, Interaction, Object
from discord.app_commands import Choice, Group, autocomplete, command
from discord.ext.commands import Bot, Cog

class Developer(Cog):
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

	@cog.command(name = "enable", description = "Load a cog to the bot's runtime")
	@autocomplete(extension = unloaded_extension_list)
	async def enable(self, interaction: Interaction, extension: str):
		try:
			await self.bot.load_extension(f"cogs.{extension}")
			await interaction.response.send_message(
				f"{self.bot.metadata.get('EMOJI_SUCCESS')} Loaded `cogs.{extension}` extension"
			)
		except Exception as error:
			await interaction.response.send_message(
				f"{self.bot.metadata.get('EMOJI_FAIL')} Unable to load `cogs.{extension}`\n```python\n{error}\n```",
				ephemeral = True
			)

	@cog.command(name = "disable", description = "Unload a cog from the bot's runtime")
	@autocomplete(extension = loaded_extension_list)
	async def disable(self, interaction: Interaction, extension: str):
		if extension == "developer":
			return await interaction.response.send_message(f"{self.bot.metadata.get('EMOJI_FAIL')} Unloading `cogs.{extension}` is disallowed")
		try:
			await self.bot.unload_extension(f"cogs.{extension}")
			self.bot.loaded_extension_list.remove(extension)
			await interaction.response.send_message(
				f"{self.bot.metadata.get('EMOJI_SUCCESS')} Unloaded `cogs.{extension}` extension"
			)
		except Exception as error:
			await interaction.response.send_message(
				f"{self.bot.metadata.get('EMOJI_FAIL')} Unable to unload `cogs.{extension}`\n```python\n{error}\n```",
				ephemeral = True
			)

	@cog.command(name = "restart", description = "Unload a cog from bots runtime to load updated code")
	@autocomplete(extension = loaded_extension_list)
	async def restart(self, interaction: Interaction, extension: str):
		try:
			await self.bot.reload_extension(f"cogs.{extension}")
			await interaction.response.send_message(
				f"{self.bot.metadata.get('EMOJI_SUCCESS')} Reloaded `cogs.{extension}` extension"
			)
		except Exception as error:
			await interaction.response.send_message(
				f"{self.bot.metadata.get('EMOJI_FAIL')} Unable to reload `cogs.{extension}`\n```python\n{error}\n```",
				ephemeral = True
			)

	@cog.command(name = "reboot", description = "Reloads all the cogs.")
	async def reboot(self, interaction: Interaction):
		for extension in self.bot.loaded_extension_list:
			await self.bot.unload_extension(f"cogs.{extension}")
			self.bot.loaded_extension_list.remove(extension)
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

		unloaded_extensions = [
			extension
			for extension in [
				extension[:-3]
				for extension in os.listdir("./cogs") if extension.endswith(".py")
			] if extension not in self.bot.loaded_extension_list
		]

		embed = Embed(
			description = "# Reloaded All Cog Extensions",
			colour = 0x2B2D31
		).add_field(
			name = "> Loaded",
			value = "```diff\n" + "\n".join(f"+ {ext}" for ext in self.bot.loaded_extension_list) + "\n```",
			inline = False
		)

		if self.bot.unloaded_extensions_list != []:
			embed.add_field(
				name = "> Failed to load",
				value = "```diff\n" + "\n".join(f"- {ext}" for ext in unloaded_extensions) + "\n```",
				inline = True
			)

		await interaction.response.send_message(embed = embed)

	@command(name = "health", description = "Check the bot's developer information.")
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
		efficiency_description = "peak" if ping <= 50 and len(unloaded_extensions) == 0 else ("critical" if self.bot.internal_error_occured else "degraded")
		status = "critical-health" if self.bot.internal_error_occured else ("degraded-health" if len(unloaded_extensions) > 0 or ping >= 125 else "good-health")
		ping_emoji = self.bot.metadata.get('EMOJI_GOODPING') if ping <= 50 else (self.bot.metadata.get('EMOJI_MODERATEPING') if ping <= 125 else self.bot.metadata.get('EMOJI_BADPING'))
		
		embed = Embed(
			description = f"Running build `{self.bot.build}` with `{efficiency_description}` performance",
			colour = 0x2B2D31
		).add_field(
			name = "> Ping",
			value = f"{ping_emoji} `{ping}ms`",
			inline = True
		).add_field(
			name = "> Servers",
			value = f"`{len(self.bot.guilds)}` *(`{len(self.bot.users)}` members)*",
			inline = True
		).add_field(
			name = "> Loaded",
			value = "```diff\n" + "\n".join(f"+ {ext}" for ext in self.bot.loaded_extension_list) + "\n```",
			inline = False
		).add_field(
			name = "> Unloaded",
			value = "```diff\n" + "\n".join(f"- {ext}" for ext in unloaded_extensions) + "\n```",
			inline = True
		).set_author(
			name = "Health Status",
			icon_url = f"https://cdn.uwitz.org/r/{status}.png"
		)

		await interaction.response.send_message(embed = embed)

async def setup(bot: Bot):
	await bot.add_cog(Developer(bot), guild = Object(bot.metadata.get("GUILD")))